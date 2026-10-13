# Operations and deployment

## Development

```bash
cp .env.example .env
# Replace each secret with a unique randomly generated strong value.
docker compose up --build -d
docker compose logs -f api
```

Database is on a persistent Docker named volume. In production use managed PostgreSQL with point-in-time recovery; do not treat the local volume as a durable national record.

### Using the JSON API
1. Submit POST /v1/datasets as INGEST with a JSON `{"source": "...", "economy": {...}}` payload.
2. Approve POST /v1/datasets/1/approve independently with REVIEWER_A and REVIEWER_B.
3. Run POST /v1/plans as PLANNER and verify result input_sha256 and numerical balance checks.
4. Inspect /v1/datasets, /v1/status and /v1/plans/1.

All writes are advisory; no production orders exist.

### Public information pipeline

GitHub's weekly `public-data-refresh` job fetches World Bank API indicators into a short-lived workflow artifact, retaining the raw response hash in the resulting JSON for reproducibility. It DOES NOT auto-promote data into planning parameters. Persistent import runs against a *separately provisioned* database via `python -m cmpe.worldbank --country USA --import-db` with CMPE_DATABASE_URL. Schedule that command on a trusted service inside the DB's private network, not a public runner containing national database credentials.

### Reliability

For a hosted system add reverse proxy/TLS, database migrations, persistent queue, object storage, regional replicas, observability, SLOs, encrypted backups and restore drills. GitHub Actions workers cannot keep the API alive when a job ends. CI passing is not proof of real-world planning accuracy.

### Costs and requirements

A small development pilot using an existing Postgres instance, single container instance and object-storage bucket can be in the tens to hundreds of dollars per month before labor; deployed secure ingestion, staffed audits and regional integration dominate real costs. Model actual prices after choosing a country, data volumes, number of reporting institutions, RPO/RTO, legal requirements, network connectivity, retention and availability target. This repository does not claim a validated national cost estimate.
