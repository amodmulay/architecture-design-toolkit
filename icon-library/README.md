# Icon Library

A curated local catalogue of vendor, platform, and generic architecture icons.

## Directory conventions

- `aws/`, `azure/`, `gcp/`, `kubernetes/`
- `databases/`, `messaging/`, `ai/`, `generic/`

Use descriptive, stable filenames (for example `azure-cosmos-db.svg`). Keep original vendor names where required by the source pack.

## Sources

Prefer official icon packs:
- AWS Architecture Icons: https://aws.amazon.com/architecture/icons/
- Microsoft Azure Architecture Icons: https://learn.microsoft.com/azure/architecture/icons/
- Google Cloud Architecture Center: https://cloud.google.com/icons
- Kubernetes project artwork: https://github.com/kubernetes/kubernetes/tree/master/logo
- Simple Icons: https://simpleicons.org/
- Iconify: https://iconify.design/

Check each source's current terms before redistributing assets. Publicly downloadable does not automatically mean MIT-licensed or freely redistributable.

## Manifest

Register every third-party asset in `manifest.json` with `id`, `name`, `provider`, `path`, `source_url`, `license`, `attribution`, `retrieved_on`, and `notes`.

Do not add assets without provenance. If license terms are unclear, link to the source rather than committing the asset until redistribution is confirmed.
