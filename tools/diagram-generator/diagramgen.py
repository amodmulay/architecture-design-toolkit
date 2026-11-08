#!/usr/bin/env python3
"""Generate editable diagrams.net XML from the toolkit's canonical architecture JSON."""
from __future__ import annotations

import argparse
import base64
import json
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from xml.sax.saxutils import escape

LAYERS = ["users", "channels", "edge", "api", "application", "services", "integration", "data", "ai", "operations", "security"]


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
    for item in model["components"]:
        boundary = item.get("boundary")
        if boundary and boundary not in boundary_ids:
            raise ValueError(f"Component {item['id']} references unknown boundary: {boundary}")


def safe_text(value: str) -> str:
    return escape(str(value), {'"': "&quot;"})


def resolve_icon(icon_id: str | None, icon_root: Path) -> str | None:
    if not icon_id:
        return None
    # Accept an exact repository-relative path or an unambiguous filename/stem.
    candidate = (icon_root / icon_id).resolve()
    root = icon_root.resolve()
    if candidate.is_file() and root in candidate.parents and candidate.suffix.lower() == ".svg":
        return candidate.read_text(encoding="utf-8")
    matches = list(icon_root.rglob(icon_id if icon_id.endswith(".svg") else icon_id + ".svg"))
    if not matches:
        matches = [p for p in icon_root.rglob("*.svg") if p.stem == icon_id]
    return matches[0].read_text(encoding="utf-8") if len(matches) == 1 else None


def svg_data(svg: str) -> str:
    return "data:image/svg+xml;base64," + base64.b64encode(svg.encode("utf-8")).decode("ascii")


def build_drawio(model: dict, icon_root: Path | None = None) -> str:
    validate_model(model)
    icon_root = icon_root or Path("icon-library")
    components = model["components"]
    boundaries = model.get("boundaries", [])
    boundary_map = {b["id"]: b for b in boundaries}

    # Components without an explicit boundary are placed in a generated system lane.
    lanes: dict[str, list[dict]] = {}
    for component in components:
        lane = component.get("boundary") or "__system__"
        lanes.setdefault(lane, []).append(component)
    lane_ids = list(lanes)
    lane_height = 210
    lane_gap = 26
    left = 50
    top = 90
    node_gap = 52
    default_w, default_h = 210, 104
    max_columns = max((len(items) for items in lanes.values()), default=1)
    canvas_width = max(900, left * 2 + max_columns * default_w + max(0, max_columns - 1) * node_gap)
    canvas_height = top + len(lane_ids) * (lane_height + lane_gap) + 70

    root = ET.Element("mxfile", {"host": "app.diagrams.net", "modified": "2026-11-08T00:00:00.000Z", "agent": "architecture-design-toolkit", "version": "24.7.17", "type": "device"})
    diagram = ET.SubElement(root, "diagram", {"id": "architecture", "name": model["name"]})
    graph = ET.SubElement(diagram, "mxGraphModel", {"dx": str(canvas_width), "dy": str(canvas_height), "grid": "1", "gridSize": "10", "guides": "1", "tooltips": "1", "connect": "1", "arrows": "1", "fold": "1", "page": "1", "pageScale": "1", "pageWidth": str(canvas_width), "pageHeight": str(canvas_height), "math": "0", "shadow": "0"})
    cells = ET.SubElement(graph, "root")
    ET.SubElement(cells, "mxCell", {"id": "0"})
    ET.SubElement(cells, "mxCell", {"id": "1", "parent": "0"})

    positions: dict[str, tuple[int, int, int, int]] = {}
    lane_y: dict[str, int] = {}
    for lane_index, lane_id in enumerate(lane_ids):
        y = top + lane_index * (lane_height + lane_gap)
        lane_y[lane_id] = y
        boundary = boundary_map.get(lane_id, {"title": model["name"], "type": "System"})
        lane_title = boundary.get("title", lane_id)
        lane_style = "rounded=1;whiteSpace=wrap;html=1;fillColor=#f7f9fc;strokeColor=#b8c4d6;dashed=1;verticalAlign=top;spacingTop=10;fontStyle=1;fontSize=14;"
        lane_cell = ET.SubElement(cells, "mxCell", {"id": "lane_" + lane_id, "value": safe_text(lane_title), "style": lane_style, "vertex": "1", "parent": "1"})
        ET.SubElement(lane_cell, "mxGeometry", {"x": str(left - 20), "y": str(y), "width": str(canvas_width - left), "height": str(lane_height), "as": "geometry"})
        for col, component in enumerate(lanes[lane_id]):
            width = int(component.get("width", default_w))
            height = int(component.get("height", default_h))
            x = left + col * (default_w + node_gap)
            node_y = y + 76
            positions[component["id"]] = (x, node_y, width, height)
            title = safe_text(component["title"])
            responsibility = safe_text(component["responsibility"])
            tech = component.get("technology") or component.get("provider") or ""
            subtitle = safe_text(tech)
            label = f"<b>{title}</b><br><font style=\"font-size:10px\">{responsibility}</font>"
            if subtitle:
                label += f"<br><font style=\"font-size:9px;color:#52606d\">{subtitle}</font>"
            style = "rounded=1;whiteSpace=wrap;html=1;fillColor=#ffffff;strokeColor=#526d91;strokeWidth=1.5;align=center;verticalAlign=middle;spacing=8;fontSize=13;"
            icon = resolve_icon(component.get("icon_id"), icon_root)
            if icon:
                style += "image=" + svg_data(icon) + ";imageWidth=32;imageHeight=32;imageAlign=left;imageVerticalAlign=top;spacingLeft=42;"
            node = ET.SubElement(cells, "mxCell", {"id": "component_" + component["id"], "value": label, "style": style, "vertex": "1", "parent": "1"})
            ET.SubElement(node, "mxGeometry", {"x": str(x), "y": str(node_y), "width": str(width), "height": str(height), "as": "geometry"})

    for edge in model["connections"]:
        sx, sy, sw, sh = positions[edge["source"]]
        tx, ty, tw, th = positions[edge["target"]]
        # Right-to-left orthogonal routing, with a reserved midpoint lane.
        start_x, start_y = sx + sw, sy + sh // 2
        end_x, end_y = tx, ty + th // 2
        mid_x = (start_x + end_x) // 2
        style = "edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;endArrow=block;endFill=1;strokeWidth=1.5;"
        mode = edge.get("mode", "unknown")
        if mode in ("async", "stream", "batch"):
            style += "dashed=1;"
        edge_label = safe_text(edge["label"])
        if edge.get("protocol"):
            edge_label += "<br><font style=\"font-size:9px\">" + safe_text(edge["protocol"]) + "</font>"
        cell = ET.SubElement(cells, "mxCell", {"id": "connection_" + edge["id"], "value": edge_label, "style": style, "edge": "1", "parent": "1", "source": "component_" + edge["source"], "target": "component_" + edge["target"]})
        geometry = ET.SubElement(cell, "mxGeometry", {"relative": "1", "as": "geometry"})
        points = ET.SubElement(geometry, "Array", {"as": "points"})
        ET.SubElement(points, "mxPoint", {"x": str(mid_x), "y": str(start_y)})
        ET.SubElement(points, "mxPoint", {"x": str(mid_x), "y": str(end_y)})

    ET.indent(root, space="  ")
    return ET.tostring(root, encoding="unicode", xml_declaration=True)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("model", type=Path, help="Architecture model JSON file")
    parser.add_argument("--out", type=Path, help="Output .drawio path (default: model name)")
    parser.add_argument("--icons", type=Path, default=Path("icon-library"), help="Local icon catalogue root")
    parser.add_argument("--validate-only", action="store_true", help="Validate model without generating a diagram")
    args = parser.parse_args()
    try:
        model = load_model(args.model)
        if args.validate_only:
            print(f"Valid architecture model: {len(model['components'])} components, {len(model['connections'])} connections")
            return 0
        output = args.out or args.model.with_suffix(".drawio")
        output.parent.mkdir(parents=True, exist_ok=True)
        xml = build_drawio(model, args.icons)
        # Parse the emitted XML before writing it.
        ET.fromstring(xml)
        output.write_text(xml, encoding="utf-8")
        print(f"Generated editable Draw.io diagram: {output}")
        return 0
    except (ValueError, OSError, ET.ParseError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
