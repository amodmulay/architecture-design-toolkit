# Icon Library

A curated local catalogue of vendor, platform, product, and generic architecture icons. Assets are stored locally so generated diagrams do not depend on remote URLs.

## Sources and terms

Prefer official architecture packs for service/product icons:
- [AWS Architecture Icons](https://aws.amazon.com/architecture/icons/) — AWS permits customers and partners to use its toolkits/assets for architecture diagrams and related technical materials. Review current AWS terms before redistribution.
- [Microsoft Azure Architecture Icons](https://learn.microsoft.com/azure/architecture/icons/) — Microsoft permits use in architecture diagrams, training materials, or documentation subject to its icon terms; other rights are reserved.
- [Google Cloud Icons](https://cloud.google.com/icons) — official product and category icon downloads.
- [Kubernetes artwork](https://github.com/kubernetes/kubernetes/tree/master/logo) — review repository artwork and trademark guidance.
- [Simple Icons](https://simpleicons.org/) — useful for vendor/technology brand marks. The project is CC0, but its disclaimer makes clear that artwork licensing does not waive trademark rights and individual icon metadata should be checked.
- [Iconify](https://iconify.design/) — useful discovery/catalogue layer; check the underlying collection's license, not merely Iconify's platform license.

## Use the CLI

See [tools/icon-catalogue/README.md](../tools/icon-catalogue/README.md). It can fetch individual SVGs, import official ZIPs, normalize SVG structure, hash/deduplicate assets, and audit provenance.

## Directory conventions

Assets are stored by provider/category, for example `aws/`, `azure/`, `gcp/`, `kubernetes/`, `databases/`, `messaging/`, `ai/`, and `generic/`.

## Manifest

Every asset must have `id`, `name`, `provider`, `path`, `source_url`, `license`, `retrieved_on`, and `sha256`. Add license URL and attribution whenever available. Do not infer a license from the fact that an asset is downloadable.

## Important

The repository's MIT license applies to original toolkit code and documentation, not automatically to third-party logos/icons. Brand names and marks may be trademarks even when SVG artwork is permissively licensed.
