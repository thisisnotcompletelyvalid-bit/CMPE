# CMPE: national physical-information acquisition and governance specification
Version 0.2 | Scope: technical research and advisory applications, **not national operational authorization**.

## Why data must be multilayered
No single information feed contains the information necessary to plan a modern economy. Aggregate money-based input-output tables cannot be mistaken for physical recipes. Physical recipes cannot establish household needs; national averages conceal regional deprivation; accurate factory inventories do not measure workplace safety, ecological obligations or public consent.

Build four linked but separated models:
1. Material account: commodity IDs, physical stock and flow, technological input matrices, services and capital renewal, network logistics, external trade.
2. Social needs account: minimum needs, service access, distribution by geographic cohorts, labor limits, accessibility, unpaid social reproduction, grievance/choice feedback.
3. Ecological account: energy carriers, freshwater basins, emissions and sinks, finite resource stocks, ecosystem regeneration limits, disaster resilience.
4. Institutions account: who controls priorities, independent audit, workers' technical feedback, limits on surveillance, appeals, model governance and lawful corrections.

Their compatibility is an empirical question. Catalog requirements in `cmpe/catalog.py` are the initial checklist of **27** domains and reporting standards; none is certified complete in this prototype.

## Full national data contract

Every physically modeled flow requires: source organization and authorizing credential, physical commodity taxonomy, technology/process and site, region and jurisdiction, period start/end with timezone, quantity with unit and dimension, direct observation versus imputed/estimated status, uncertainty interval, revision ID, provenance and versioned transformation, spatial sampling coverage, licensing and confidentiality class.

Each asset requires maintenance obligations, age, capacity, useful life, downtime and replacement constraints. Each transformation requires stoichiometric/engineering input-output coefficients, labor-hour skill vectors, energy carrier consumption, emissions and byproducts, usable-yield/quality distributions, inventory delay and transportation feasibility. Services require quality/outcome indicators in addition to volume.

No amount of post-hoc AI inference can reconstruct these variables with guaranteed validity without adequate measurement.

## Federated institutional topology

Local sources (facilities, utilities, farms, warehouses, hospitals, municipalities and surveys) -> authenticated source gateways -> immutable signed raw evidence -> schema, unit and source validation -> automatic anomaly + double-entry stock/flow reconciliation -> independent field/audit sampling -> quarantine + two-person approval -> approved analytical lake -> regional stock/flow balance -> national interregional reconciliation -> scenario planning -> worker/community public challenge -> authorized non-actuating plan recommendation.

A federated physical data model keeps fine-grained personal and facility-sensitive data at its legal origin. National nodes receive aggregates subject to threshold suppression and purpose limitation, plus verifiable proofs/attestations. Independent public institutions oversee retention, correction requests, redaction and citizen appeal. Disallow government surveillance of individuals for economic optimization.

## Concrete collection schedule and safeguards

- **Sub-hourly**: electrical generation, demand and transmission status. Validate using independent settlement meters and conservation.
- **Daily**: critical inventories, dispatch/receipts, hospital critical capacity, food and fuel distribution, emergency reserves. Warehouse stock equation S(t+1)=S(t)+receipts-shipments-waste-corrections.
- **Weekly**: agricultural outputs, maintenance availability, workplace labor, transport constraints, material quality.
- **Monthly**: production coefficients, equipment condition and service accessibility, sampled household needs and labor conditions.
- **Quarterly/yearly**: representative needs surveys, capital stock census, resource assessments, time-use and ecological conditions.

**One direction of control:** unsigned, invalid, contradictory or unreviewed measurements remain quarantined; they are not silently promoted into the solver. If sources disagree, the system produces an uncertainty and reconciliation incident, not a manufactured national total.

### Audit design
- Signed identities: unique rotating Ed25519 facility/organization keys stored in hardware-backed key systems; TLS/mTLS for transmission; revocation, rekeying, access expiry and replay prevention.
- Truthfulness: verify units and method calibration, random physical site visits, warehouse and generation balance equations, capture-recapture surveys, multiple independent measurement sources, public worker corrections and protected reporting channels. A signature verifies the reporter, **not truth**.
- Anti-Goodhart: monitor quality and harm alongside volume; sample metrics not tied to rewards; independent institution assesses manipulation incentives.
- Privacy: no individual health, immigration, payroll or consumption logs in the national optimizer. Only lawfully processed aggregates; suppress small cohorts and introduce appropriate privacy review.
- Democratic accountability: publish scenario assumptions, infeasibility certificates and appeals; review boards separated from operators and economic institutions; prohibit autonomous critical-infrastructure actuation.
- Resilience: regional contingency stock, offline operations, tested restore drills, independent immutable log anchors, multiple supply chain paths, regional failover with safe defaults.
- Software supply chain: CI tests, signed releases, pinned dependencies, independent pen testing, vulnerability response, disaster rehearsals, external audits.

## Source program / calibration approach

Start with official public aggregate datasets (BEA national supply/use monetary tables, US EIA electricity physical quantities, NOAA/USGS environmental measurements, BLS labor data, FAOSTAT food balances, UN SEEA natural-resource accounts, OECD ICIO inter-country intermediate production). Maintain source granularity and separate currencies from physical units. Source adapter certification requires independent totals, missingness coverage, checksum-based reproducibility, unit conversions, published schema and plausible variance bounds.

The current World Bank historical CO2 and electricity access feed is **context**, not a calibrated industrial input-output model. The first high-value industrial calibration should be EIA electricity generation vs demand, constrained by installed generating capacity, regional transmission and fuel availability.

## Quantitative acceptance gates

**G0 Research:** deterministic tests; synthetic fixtures; no operational impact.
**G1 Public statistical observatory:** authentic licensed public series, date and provider labels, verifiable source hash, automated checks, no inference of missing records.
**G2 Controlled regional pilot:** registered and signed sources; independent double-entry reconciliation; stratified site audits; data quality dashboards; no direct actuator commands; two independently authorized reviewers.
**G3 Regional advisory optimization:** skill/material/energy/inventory constraints, independently verified input-output balances, documented forecast errors, shortage failover, appeals, human-authorized plans.
**G4 National advisory federation:** multiple independent regions and auditors; disaster recovery; secure representative needs collection; interregional trade conservation; thousands/millions of activities with disclosed solver performance; public democratic oversight; comprehensive legal and security reviews.
**G5 National operational authority:** *Not implemented or authorized.* Requires entirely separate political, legal, economic, security and democratic decisions. Never label G0-G4 as abolition of commodity production or the law of value.

### Evidentiary burden for declaring readiness
- All 28 catalog requirements have multi-source verifications, current coverage and audited uncertainty bounds.
- No essential unmet need hidden by aggregate success statistics.
- Every material balance closes within physically defensible uncertainty ranges; unexplained residuals trigger adjudication.
- Plans meet legal safety and environmental constraints under shocks, and can be reproduced from pinned inputs and solver version.
- Public representatives can challenge priorities and inspect non-sensitive allocations without privileged system access.
- Independent certification and restore testing repeated on schedule.

## Provisional capacity and costs

Pilot scale (e.g., 10-100 source institutions): 1 DB, small message service, object storage, two independent reviewers and field-audit program. Main cost is professional labor and independent verification, not matrices.

Regional scale (thousands of reporting organizations): clustered Postgres metadata and partitioned analytic data; signed durable streaming, storage lifecycle, field inspectors, redundant networking, dedicated solver workers, uncertainty studies.

National scale (potentially millions of source streams): regional federation with dedicated data sovereignty, audit processes, large object stores, transactional metadata, high-throughput columnar lakehouse, disaster recovery, special sector-specific solvers, independent security governance.

No fixed credible national dollar total can be inferred without country size, facility count, reporting frequencies, instrumentation, salaries, resilience tier, data sovereignty, availability targets and regulations. Never equate the inexpensive research web service with the national infrastructure budget.
