# CMPE · Computational Marxist Political Economy

[![CI](https://github.com/thisisnotcompletelyvalid-bit/CMPE/actions/workflows/ci.yml/badge.svg)](https://github.com/thisisnotcompletelyvalid-bit/CMPE/actions/workflows/ci.yml)

**Status: v3 alpha, research and advisory simulations only.** An open, inspectable service for physical-economic data, authenticated submissions, two-person approval and linear planning. No personal data, no automatic economic orders, no production-critical control endpoints.

## What works in this branch

- Web console and FastAPI with protected JSON endpoints.
- Relational persistence via PostgreSQL (SQLite is restricted to local tests).
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
pytest -q
python -m compileall -q cmpe
```

## Repository vs national-scale architecture

GitHub stores source code, schemas, small public fixtures, provenance and CI recipes. **It is not a high-volume national operational database.** GitHub Actions runners are temporary and workflow artifacts expire. Data-plane architecture: regional collectors -> integrity checks -> encrypted immutable object storage -> partitioned operational PostgreSQL / columnar analytical warehouse -> approved physical-economic models -> asynchronous solver workers -> advisory API and audit. Provision persistent external storage and cloud/on-prem compute separately, with independent oversight.

See [ARCHITECTURE](docs/ARCHITECTURE.md), [SECURITY](docs/SECURITY.md), and [OPERATIONS](docs/OPERATIONS.md).

## Intellectual scope

The long-term project studies the engineering conditions for democratic, increasingly nonmarket physical coordination. A numerical optimizer does not abolish commodity production or Marx's law of value. Economic transformation, property rights and decision-making institutions remain separate political and empirical problems.
