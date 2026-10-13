# Public physical-economic observatory

A continually refreshed research publication using **historical** World Bank emissions observations. This is not a live electrical dispatch system and is **not** the national planner.

## Automated publication path

1. GitHub Actions fetches `EN.ATM.CO2E.KT` (annual carbon dioxide emissions, kt) and `EG.ELC.ACCS.ZS` (electricity access percentage) for USA, CHN, DEU and IND.
2. Enforces allowlisted identifiers, exact declared units, nonnegative finite values, year bounds, absence of duplicate years and a physical-observations minimum.
3. Generates static HTML, data.json and a SHA256 check; uploads an independently inspectable artifact.
4. On main, updates the `public-data` repository branch with `latest.json` and a date-specific snapshot. Only small public curated data in Git; no private data.
5. Attempts a GitHub Pages deploy after generating a site artifact.

Enable the public website: **Repository Settings → Pages → Build and deployment → Source: GitHub Actions**. Without that setting, static artifacts and the `public-data` branch are usable but no public site can be claimed.

After successful persistence, public data URI:
`https://raw.githubusercontent.com/thisisnotcompletelyvalid-bit/CMPE/public-data/data/public/latest.json`

The latest *observed year* differs from the collection date. World Bank carbon dioxide emissions may lag by many years and must not be interpreted as live grid capacity.

## Scaling

The prototype uses separate data planes: GitHub stores software and small curated public outputs; external object storage holds raw versioned data; managed PostgreSQL holds metadata and approved model states; warehouse and solver clusters handle bulk transformations and sparse optimization. Industrial-report feeds require verified identities, signed events, reconciliation, retention protection, throughput limits, review procedures, independently anchored audit trails, privacy law review and independent security testing.

Optional `CMPE_ARCHIVE_BUCKET` points to an S3-compatible evidence archive (in a trusted worker, not GitHub PR jobs). Object Lock, encryption controls, backup, secrets and IAM must be provisioned separately.

Crucially no public observation automatically becomes a production technology coefficient or a planning instruction.

Data licensing: World Bank metadata identifies Climate Watch as an underlying provider for some emissions series and may impose noncommercial license terms. Preserve attribution and verify current reuse rights before production or commercial redistribution.
