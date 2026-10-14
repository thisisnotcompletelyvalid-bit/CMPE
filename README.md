# CMPE · Computational Marxist Political Economy

[![CI](https://github.com/thisisnotcompletelyvalid-bit/CMPE/actions/workflows/ci.yml/badge.svg)](https://github.com/thisisnotcompletelyvalid-bit/CMPE/actions/workflows/ci.yml)

**Status: v3 alpha, research and advisory simulations only.** An open, inspectable service for physical-economic data, authenticated submissions, two-person approval and linear planning. No personal data, no automatic economic orders, no production-critical control endpoints.

## Public physical-economy observatory (automated)

A separate read-only public report now validates official historical physical carbon-dioxide emissions in **Mt CO₂e**, excluding land-use change, and electricity access for USA, China, Germany and India.

- [Publication workflow](https://github.com/thisisnotcompletelyvalid-bit/CMPE/actions/workflows/site-publish.yml): verifies the live World Bank API and publishes dated, SHA-256-checked data snapshots every Tuesday.
- [Persistent small public-data snapshots](https://github.com/thisisnotcompletelyvalid-bit/CMPE/tree/public-data/data/public): GitHub branch, usable as static JSON. **Not** suitable for high-volume or sensitive national data.
- [Static dashboard](https://thisisnotcompletelyvalid-bit.github.io/CMPE/): only live when GitHub Pages has been enabled in repository **Settings → Pages → Source: GitHub Actions** and the deploy job is successful.
- [Source and retention rules](docs/PUBLIC_OBSERVATORY.md).

Run `python -m cmpe.public_report --out site-build` to independently reconstruct the public site; for offline deterministic smoke tests use `--demo` (clearly labeled fictional).
Historical observations are not live energy generation measurements, input-output coefficients or national production data. The archived World Bank electricity-generation indicator was rejected by the current source API, so this release uses a newer EDGAR/JRC emissions series and does **not** claim a calibrated electricity grid.

Persistent server deployments require an independently provisioned VM or container service, a database and secured storage. GitHub Actions is not an always-on web server.

## What works in this branch

- Web console and FastAPI with protected JSON endpoints.
- Relational persistence via PostgreSQL (SQLite is restricted to local tests), with an Alembic initial migration and a container startup migration gate.
- Validated, explicit-unit input-output model, bounded inputs and deterministic SciPy/HiGHS planning.
- Two distinct reviewer credentials are required before any dataset becomes active.
- Public World Bank indicator importer that keeps national statistics separate from technical production coefficients.
- GitHub Actions CI (tests, compile and Docker build) and weekly public-data fetch with artifact provenance.
- Containerized local PostgreSQL and application for reproducible operation.

**Not yet implemented:** automatic production data acquisition from real firms; validated industrial digital twins; signed institutional ingestion carried over from CMPE 2.0; durable external audit anchoring; managed SSO/MFA; key rotation; distributed compute queues; high availability; jurisdiction-specific labor/consumer data; field verification; reliable national-scale performance. These are deployment blockers. This version makes no claim to national security certification.

## Quickstart (local research)

Copy `.env.example` to `.env`, generate five different high-entropy credentials (at least 32 characters each), and replace the placeholders. Never commit your .env or credentials.

```bash
docker compose up --build -d
curl http://127.0.0.1:8080/health/ready
```

Open http://127.0.0.1:8080. For a demonstration dataset:

```bash
curl -X POST http://127.0.0.1:8080/v1/datasets \
  -H "X-CMPE-Key: $CMPE_INGEST_TOKEN" -H 'Content-Type: application/json' \
  --data-binary @data/examples/fictional_economy.json
```

Use reviewer A and reviewer B credentials to POST `/v1/datasets/{id}/approve`, then call `POST /v1/plans` with the planner credential. Token authentication in this alpha is a scaffold, *not* a substitute for identity federation, rate limiting, mTLS, or infrastructure-level logging. Never expose it directly to the public Internet.

Fetch public annual indicators into an external database when configured:

```bash
python -m cmpe.worldbank --country USA --out data/snapshots/worldbank_USA.json --import-db
```

These indicators are not automatically promoted into production functions or planning targets.

## Running tests

```bash
pip install -r requirements.txt
python -m pytest -q
python -m compileall -q cmpe
```

## Repository vs national-scale architecture

GitHub stores source code, schemas, small public fixtures, provenance and CI recipes. **It is not a high-volume national operational database.** GitHub Actions runners are temporary and workflow artifacts expire. Data-plane architecture: regional collectors -> integrity checks -> encrypted immutable object storage -> partitioned operational PostgreSQL / columnar analytical warehouse -> approved physical-economic models -> asynchronous solver workers -> advisory API and audit. Provision persistent external storage and cloud/on-prem compute separately, with independent oversight.

See [ARCHITECTURE](docs/ARCHITECTURE.md), [SECURITY](docs/SECURITY.md), and [OPERATIONS](docs/OPERATIONS.md).

## Intellectual scope

The long-term project studies the engineering conditions for democratic, increasingly nonmarket physical coordination. A numerical optimizer does not abolish commodity production or Marx's law of value. Economic transformation, property rights and decision-making institutions remain separate political and empirical problems.


## National information acquisition (current branch)

[Data register and political-economy verification protocol](docs/NATIONAL_DATA_ACQUISITION.md) defines the physical, labor, needs, ecological, external-trade and democratic input requirements. Public `/v1/catalog` and `/v1/readiness` endpoints explicitly show missing evidence; this software **is not nationally ready**.

Registered organizations can submit signed **aggregated** physical reports to secured local research services, using Ed25519 canonical-JSON envelopes, finite typed units, source sequences, physical-balance flagging and quarantine. Two reviewers may classify non-flagged reports as reviewed, but even reviewed reports cannot become optimizer coefficients without separate economic validation. This API is **not** a production audit system: it lacks enterprise identity, external log anchoring, source key rotation, regional replication, field measurement validation, and concurrency-safe reporting ledgers.

The Render `render.yaml` Blueprint deliberately provisions a **read-only** public research interface with an experimental Free-tier database. It does not enable signed intake over the public Internet. The Free database is not a durable national evidence archive; production systems require a paid HA/PostgreSQL tier, encrypted object storage, signed institution gateways and independent governance.

Read the architecture before applying any Blueprint. There is no automatic link between public World Bank observations and physical input-output coefficients.


## Scaling calculator

`GET /v1/capacity` calculates data ingress, peak event rate, storage retention and optional user-supplied storage-only unit rates. The solver now uses SciPy sparse CSR matrices and has a 451-activity automated test, but there is no claim of readiness for 100,000+ activities, distributed optimization, national input-output completeness, or continuous national operations. Consult `docs/NATIONAL_DATA_ACQUISITION.md` for all research gates.
