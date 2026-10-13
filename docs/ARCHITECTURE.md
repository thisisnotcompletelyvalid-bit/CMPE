# CMPE Architecture: active research -> regional pilots -> national advisory federation

## Architecture boundaries

1. **GitHub: development control plane.** Code, schemas, public small fixtures, reproducibility manifests, security reviews, releases, CI. Never commit personal records, source private keys, raw industrial production logs, or national economic databases.
2. **Data acquisition regions.** Authenticated reporting organizations, metered systems and third-party statistical agencies publish signed, versioned, timestamped measurements and standardized unit contracts. A signature proves identity and integrity, not truth. Reconciliation to invoices, meters, inventories, field inspections and independent reports is mandatory.
3. **Durable object storage.** Encrypt raw, append-only submissions using regional object-store retention locks and independently managed keys. Record SHA-256, source identity, collection timestamp, consent/legal basis, schema version, unit definitions, processing code version, and revisions.
4. **Operational metadata database.** Managed PostgreSQL, transactionally recording provenance, approvals, observation references, plan versions, and audit trails. Production requires migrations and PITR; prototype uses SQLAlchemy create_all bootstrap only.
5. **Analytic warehouse.** Partitioned Parquet/Arrow in object storage plus DuckDB/ClickHouse/Spark/Trino for large physical flow matrices. In-memory Python arrays are not a substitute for national-scale analytical infrastructure.
6. **Optimization tier.** Containerized worker pool with quotas and separately approved inputs. Sparse optimization, decomposition by sector/region, multi-period inventory and investment, uncertainty quantification, external verification. Stage production proposals without automated actuators.
7. **Human governance.** Producers correct their records, statistical auditors verify, two independent reviewers approve datasets, public institutions set priorities, workers and communities challenge outcomes, and planners can only simulate against approved data.

## Scalable data contracts

A quantity must include a commodity identifier, unit, location, period, producing facility, activity, flow direction, uncertainty bounds, source id, source digest, licensing/access class, and reporting method. Measurement and inference must be separate. Catalog and version official data sources; use time-stamped revisions; prohibit silent historical overwrites.

**Current reference contracts are deliberately small:** unit-bearing aggregate technologies, a vector of needs, activity input/output coefficients, labor and emissions. World Bank population/GDP/electricity-access indicators are public contextual statistics, not production recipe inputs. A future signed physical-event transport must be integrated from CMPE 2.0 after independent security review.

## Throughput and reliability roadmap

Pilot: 10-100 sources, one DB, simulated plans, daily snapshots.
Regional: thousands of data producers, dedicated ingestion brokers, object store, partitioning, dedicated validation and solver queues, replicated DB, robust backups, regional disaster recovery.
National: federation of regional nodes, geographically replicated encrypted storage, formal schemas and revision logs, independent audit anchoring, multiple optimization clusters, backpressure, fault domains, simulated failover, controlled contingency operations.

**No national-scale performance claim is made for the current alpha.** Capacity planning must benchmark worst-case ingest rate, peak events/sec, query SLA, full rebuild duration, long-horizon solver latency, data quality, and regional network partition recovery.

## Mathematical scope today

For goods g and activities a, net technology matrix B_ga = outputs_ga - inputs_ga. Optimize maximum uniform essential-needs fulfillment q in [0,1] subject to B x >= q needs; activity capacities; labor and emissions budgets. Secondary optimization minimizes labor at fixed q. Explicit post-solve feasibility checks. This is a static LP for research, not a price-based national plan and not a multi-period national digital twin.

Next: stock/flow separation, capital depreciation, investment, lead times, region-specific networks, skills, household care, embodied emissions, needs disaggregation, alternative technologies, bounds for uncertain coefficients, audit-ready shadow prices and democratic goal selection.
