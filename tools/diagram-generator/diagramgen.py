#!/usr/bin/env python3
"""Generate editable diagrams.net XML from the toolkit's canonical architecture JSON."""
from __future__ import annotations

import argparse
import base64
import json
import re
import sys
import xml.etree.ElementTree as ET
from collections import defaultdict, deque
from pathlib import Path
from xml.sax.saxutils import escape

DEFAULT_WIDTH, DEFAULT_HEIGHT = 210, 104
NODE_GAP_X, NODE_GAP_Y = 64, 36
LANE_GAP, LANE_PADDING = 28, 24
TOP, LEFT = 100, 54


def load_model(path: Path) -> dict:
    try:
        model = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"Cannot read architecture model: {exc}") from exc
    validate_model(model)
    return model


def validate_model(model: dict) -> None:
    if not isinstance(model, dict):
        raise ValueError("Model root must be a JSON object")
    for key in ("name", "components", "connections"):
        if key not in model:
            raise ValueError(f"Missing required property: {key}")
    if not isinstance(model["name"], str) or not model["name"].strip():
        raise ValueError("'name' must be a non-empty string")
    if not isinstance(model["components"], list) or not isinstance(model["connections"], list):
        raise ValueError("'components' and 'connections' must be arrays")

    component_ids = set()
    for item in model["components"]:
        if not isinstance(item, dict):
            raise ValueError("Every component must be an object")
        for key in ("id", "title", "responsibility"):
            if not isinstance(item.get(key), str) or not item[key].strip():
                raise ValueError(f"Component requires non-empty '{key}'")
        if not re.fullmatch(r"[A-Za-z][A-Za-z0-9_-]*", item["id"]):
            raise ValueError(f"Invalid component id: {item['id']}")
        if item["id"] in component_ids:
            raise ValueError(f"Duplicate component id: {item['id']}")
        component_ids.add(item["id"])
        for dimension in ("width", "height"):
            if dimension in item and (not isinstance(item[dimension], int) or item[dimension] < 70):
                raise ValueError(f"Component {item['id']} has invalid {dimension}")

    boundary_ids = set()
    for boundary in model.get("boundaries", []):
        if not isinstance(boundary, dict) or not boundary.get("id") or not boundary.get("title"):
            raise ValueError("Each boundary requires id and title")
        if boundary["id"] in boundary_ids:
            raise ValueError(f"Duplicate boundary id: {boundary['id']}")
        boundary_ids.add(boundary["id"])

    connection_ids = set()
    for edge in model["connections"]:
        if not isinstance(edge, dict):
            raise ValueError("Every connection must be an object")
        for key in ("id", "source", "target", "label"):
            if not isinstance(edge.get(key), str) or not edge[key].strip():
                raise ValueError(f"Connection requires non-empty '{key}'")
        if edge["id"] in connection_ids:
            raise ValueError(f"Duplicate connection id: {edge['id']}")
        connection_ids.add(edge["id"])
        if edge["source"] not in component_ids or edge["target"] not in component_ids:
            raise ValueError(f"Connection {edge['id']} references an unknown component")
        if edge["source"] == edge["target"]:
            raise ValueError(f"Connection {edge['id']} cannot connect a component to itself")
        if edge.get("mode", "unknown") not in ("sync", "async", "batch", "stream", "unknown"):
            raise ValueError(f"Connection {edge['id']} has an unsupported mode")
    for item in model["components"]:
        boundary = item.get("boundary")
        if boundary and boundary not in boundary_ids:
            raise ValueError(f"Component {item['id']} references unknown boundary: {boundary}")


def safe_text(value: str) -> str:
    return escape(str(value), {'"': "&quot;"})


def resolve_icon(icon_id: str | None, icon_root: Path) -> str | None:
    if not icon_id:
        return None
    root = icon_root.resolve()
    candidate = (icon_root / icon_id).resolve()
    if candidate.is_file() and root in candidate.parents and candidate.suffix.lower() == ".svg":
        return candidate.read_text(encoding="utf-8")
    matches = list(icon_root.rglob(icon_id if icon_id.endswith(".svg") else icon_id + ".svg"))
    if not matches:
        matches = [p for p in icon_root.rglob("*.svg") if p.stem == icon_id]
    return matches[0].read_text(encoding="utf-8") if len(matches) == 1 else None


def svg_data(svg: str) -> str:
    return "data:image/svg+xml;base64," + base64.b64encode(svg.encode("utf-8")).decode("ascii")


def graph_ranks(components: list[dict], edges: list[dict]) -> tuple[dict[str, int], bool]:
    """Assign longest-path ranks for DAGs; fall back safely when cycles exist."""
    ids = [c["id"] for c in components]
    outgoing = defaultdict(list)
    indegree = {node_id: 0 for node_id in ids}
    for edge in edges:
        outgoing[edge["source"]].append(edge["target"])
        indegree[edge["target"]] += 1
    queue = deque(sorted(node_id for node_id, degree in indegree.items() if degree == 0))
    ranks = {node_id: 0 for node_id in ids}
    visited = 0
    while queue:
        node = queue.popleft()
        visited += 1
        for target in sorted(outgoing[node]):
            ranks[target] = max(ranks[target], ranks[node] + 1)
            indegree[target] -= 1
            if indegree[target] == 0:
                queue.append(target)
    if visited == len(ids):
        return ranks, False

    # Cyclic graph: bounded relaxation gives a stable, approximate left-to-right order.
    ranks = {node_id: 0 for node_id in ids}
    for _ in range(max(1, len(ids))):
        changed = False
        for edge in edges:
            candidate = ranks[edge["source"]] + 1
            if candidate > ranks[edge["target"]] and candidate <= len(ids):
                ranks[edge["target"]] = candidate
                changed = True
        if not changed:
            break
    return ranks, True


def order_with_barycenter(lanes: dict[str, list[dict]], ranks: dict[str, int], edges: list[dict]) -> dict[str, list[dict]]:
    """Reduce edge crossings with deterministic neighbor-barycenter sweeps."""
    by_id = {item["id"]: item for items in lanes.values() for item in items}
    neighbors = defaultdict(list)
    for edge in edges:
        neighbors[edge["source"]].append(edge["target"])
        neighbors[edge["target"]].append(edge["source"])
    ordered = {}
    for lane_id, items in lanes.items():
        ordered[lane_id] = sorted(items, key=lambda item: (ranks[item["id"]], item["id"]))
    # Repeated sweeps are intentionally bounded; stable ID is the tie-breaker.
    for _ in range(4):
        for lane_id, items in ordered.items():
            current_pos = {item["id"]: i for i, item in enumerate(items)}
            def score(item):
                linked = [current_pos[n] for n in neighbors[item["id"]] if n in current_pos]
                return (sum(linked) / len(linked)) if linked else current_pos[item["id"]]
            items.sort(key=lambda item: (ranks[item["id"]], score(item), item["id"]))
    return ordered


def calculate_layout(model: dict) -> tuple[dict, dict, list[str]]:
    components, edges = model["components"], model["connections"]
    ranks, has_cycles = graph_ranks(components, edges)
    lanes: dict[str, list[dict]] = {}
    for component in components:
        lanes.setdefault(component.get("boundary") or "__system__", []).append(component)
    ordered = order_with_barycenter(lanes, ranks, edges)
    boundary_map = {b["id"]: b for b in model.get("boundaries", [])}

    # Rank columns are shared across lanes. Parallel components at one rank stack vertically.
    rank_widths = defaultdict(lambda: DEFAULT_WIDTH)
    for item in components:
        rank_widths[ranks[item["id"]]] = max(rank_widths[ranks[item["id"]]], int(item.get("width", DEFAULT_WIDTH)))
    rank_x = {}
    cursor = LEFT
    for rank in sorted(rank_widths):
        rank_x[rank] = cursor
        cursor += rank_widths[rank] + NODE_GAP_X

    positions = {}
    lane_geometries = {}
    y_cursor = TOP
    for lane_id, items in ordered.items():
        grouped = defaultdict(list)
        for item in items:
            grouped[ranks[item["id"]]].append(item)
        max_stack_height = max(
            (sum(int(c.get("height", DEFAULT_HEIGHT)) for c in stack) + NODE_GAP_Y * max(0, len(stack)-1)
             for stack in grouped.values()), default=DEFAULT_HEIGHT
        )
        lane_height = max(210, max_stack_height + 92)
        lane_geometries[lane_id] = (LEFT - 24, y_cursor, max(900, cursor - LEFT + 30), lane_height)
        for rank, stack in grouped.items():
            stack_height = sum(int(c.get("height", DEFAULT_HEIGHT)) for c in stack) + NODE_GAP_Y * max(0, len(stack)-1)
            node_y = y_cursor + 64 + max(0, (lane_height - 64 - stack_height) // 2)
            for item in stack:
                width, height = int(item.get("width", DEFAULT_WIDTH)), int(item.get("height", DEFAULT_HEIGHT))
                positions[item["id"]] = (rank_x[rank], node_y, width, height)
                node_y += height + NODE_GAP_Y
        y_cursor += lane_height + LANE_GAP

    warnings = []
    if has_cycles:
        warnings.append("The connection graph contains cycles; component ranks use a deterministic approximate layout.")
    for edge in edges:
        sx, sy, sw, sh = positions[edge["source"]]
        tx, ty, tw, th = positions[edge["target"]]
        if ranks[edge["source"]] == ranks[edge["target"]]:
            warnings.append(f"Connection {edge['id']} links components at the same rank; review its route.")
    return positions, lane_geometries, warnings


def edge_waypoints(source: tuple, target: tuple, edge_index: int, edge_count: int) -> tuple[str, list[tuple[int, int]]]:
    sx, sy, sw, sh = source
    tx, ty, tw, th = target
    scx, scy = sx + sw / 2, sy + sh / 2
    tcx, tcy = tx + tw / 2, ty + th / 2
    offset = (edge_index - (edge_count - 1) / 2) * 14

    if abs(tcx - scx) >= abs(tcy - scy):
        if tcx >= scx:
            source_x, target_x = sx + sw, tx
            source_y, target_y = sy + sh / 2, ty + th / 2
            middle_x = (source_x + target_x) / 2 + offset
            points = [(round(middle_x), round(source_y)), (round(middle_x), round(target_y))]
            return "exitX=1;exitY=0.5;entryX=0;entryY=0.5;", points
        source_x, target_x = sx, tx + tw
        source_y, target_y = sy + sh / 2, ty + th / 2
        middle_x = (source_x + target_x) / 2 + offset
        points = [(round(middle_x), round(source_y)), (round(middle_x), round(target_y))]
        return "exitX=0;exitY=0.5;entryX=1;entryY=0.5;", points

    if tcy >= scy:
        source_y, target_y = sy + sh, ty
        source_x, target_x = sx + sw / 2, tx + tw / 2
        middle_y = (source_y + target_y) / 2 + offset
        points = [(round(source_x), round(middle_y)), (round(target_x), round(middle_y))]
        return "exitX=0.5;exitY=1;entryX=0.5;entryY=0;", points
    source_y, target_y = sy, ty + th
    source_x, target_x = sx + sw / 2, tx + tw / 2
    middle_y = (source_y + target_y) / 2 + offset
    points = [(round(source_x), round(middle_y)), (round(target_x), round(middle_y))]
    return "exitX=0.5;exitY=0;entryX=0.5;entryY=1;", points


def build_drawio(model: dict, icon_root: Path | None = None) -> str:
    validate_model(model)
    icon_root = icon_root or Path("icon-library")
    components, edges = model["components"], model["connections"]
    positions, lane_geometries, warnings = calculate_layout(model)
    boundary_map = {b["id"]: b for b in model.get("boundaries", [])}

    max_x = max((x + w for x, y, w, h in positions.values()), default=800)
    max_y = max((y + h for x, y, w, h in positions.values()), default=600)
    canvas_width, canvas_height = max(1000, max_x + 100), max(600, max_y + 100)

    root = ET.Element("mxfile", {"host": "app.diagrams.net", "modified": "2026-11-08T00:00:00.000Z", "agent": "architecture-design-toolkit", "version": "24.7.17", "type": "device"})
    diagram = ET.SubElement(root, "diagram", {"id": "architecture", "name": model["name"]})
    graph = ET.SubElement(diagram, "mxGraphModel", {"dx": str(canvas_width), "dy": str(canvas_height), "grid": "1", "gridSize": "10", "guides": "1", "tooltips": "1", "connect": "1", "arrows": "1", "fold": "1", "page": "1", "pageScale": "1", "pageWidth": str(canvas_width), "pageHeight": str(canvas_height), "math": "0", "shadow": "0"})
    cells = ET.SubElement(graph, "root")
    ET.SubElement(cells, "mxCell", {"id": "0"})
    ET.SubElement(cells, "mxCell", {"id": "1", "parent": "0"})

    for lane_id, (x, y, width, height) in lane_geometries.items():
        boundary = boundary_map.get(lane_id, {"title": model["name"]})
        lane = ET.SubElement(cells, "mxCell", {
            "id": "lane_" + lane_id, "value": safe_text(boundary.get("title", lane_id)),
            "style": "rounded=1;whiteSpace=wrap;html=1;fillColor=#f7f9fc;strokeColor=#b8c4d6;dashed=1;verticalAlign=top;spacingTop=10;fontStyle=1;fontSize=14;",
            "vertex": "1", "parent": "1"
        })
        ET.SubElement(lane, "mxGeometry", {"x": str(x), "y": str(y), "width": str(width), "height": str(height), "as": "geometry"})

    # Edges are created before vertices so Draw.io paints them behind nodes.
    parallel_counts = defaultdict(int)
    for edge in edges:
        key = (edge["source"], edge["target"])
        parallel_counts[key] += 1
    seen_parallel = defaultdict(int)
    for edge in edges:
        key = (edge["source"], edge["target"])
        index = seen_parallel[key]
        seen_parallel[key] += 1
        anchors, waypoints = edge_waypoints(positions[edge["source"]], positions[edge["target"]], index, parallel_counts[key])
        style = "edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;endArrow=block;endFill=1;strokeWidth=1.5;" + anchors
        if edge.get("mode", "unknown") in ("async", "stream", "batch"):
            style += "dashed=1;"
        label = safe_text(edge["label"])
        if edge.get("protocol"):
            label += "<br><font style=\"font-size:9px\">" + safe_text(edge["protocol"]) + "</font>"
        cell = ET.SubElement(cells, "mxCell", {"id": "connection_" + edge["id"], "value": label, "style": style, "edge": "1", "parent": "1", "source": "component_" + edge["source"], "target": "component_" + edge["target"]})
        geometry = ET.SubElement(cell, "mxGeometry", {"relative": "1", "as": "geometry"})
        points = ET.SubElement(geometry, "Array", {"as": "points"})
        for px, py in waypoints:
            ET.SubElement(points, "mxPoint", {"x": str(px), "y": str(py)})

    for component in components:
        x, y, width, height = positions[component["id"]]
        label = "<b>" + safe_text(component["title"]) + "</b><br><font style=\"font-size:10px\">" + safe_text(component["responsibility"]) + "</font>"
        technology = component.get("technology") or component.get("provider") or ""
        if technology:
            label += "<br><font style=\"font-size:9px;color:#52606d\">" + safe_text(technology) + "</font>"
        style = "rounded=1;whiteSpace=wrap;html=1;fillColor=#ffffff;strokeColor=#526d91;strokeWidth=1.5;align=center;verticalAlign=middle;spacing=8;fontSize=13;"
        icon = resolve_icon(component.get("icon_id"), icon_root)
        if icon:
            style += "image=" + svg_data(icon) + ";imageWidth=32;imageHeight=32;imageAlign=left;imageVerticalAlign=top;spacingLeft=42;"
        node = ET.SubElement(cells, "mxCell", {"id": "component_" + component["id"], "value": label, "style": style, "vertex": "1", "parent": "1"})
        ET.SubElement(node, "mxGeometry", {"x": str(x), "y": str(y), "width": str(width), "height": str(height), "as": "geometry"})

    ET.indent(root, space="  ")
    return ET.tostring(root, encoding="unicode", xml_declaration=True)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("model", type=Path, help="Architecture model JSON file")
    parser.add_argument("--out", type=Path, help="Output .drawio path (default: model name)")
    parser.add_argument("--icons", type=Path, default=Path("icon-library"), help="Local icon catalogue root")
    parser.add_argument("--validate-only", action="store_true", help="Validate model without generating a diagram")
    parser.add_argument("--layout-report", action="store_true", help="Print layout diagnostics after generation")
    args = parser.parse_args()
    try:
        model = load_model(args.model)
        if args.validate_only:
            print(f"Valid architecture model: {len(model['components'])} components, {len(model['connections'])} connections")
            return 0
        positions, _, warnings = calculate_layout(model)
        output = args.out or args.model.with_suffix(".drawio")
        output.parent.mkdir(parents=True, exist_ok=True)
        xml = build_drawio(model, args.icons)
        ET.fromstring(xml)
        output.write_text(xml, encoding="utf-8")
        print(f"Generated editable Draw.io diagram: {output}")
        if args.layout_report:
            print(json.dumps({"components": len(positions), "connections": len(model["connections"]), "warnings": warnings}, indent=2))
        return 0
    except (ValueError, OSError, ET.ParseError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
