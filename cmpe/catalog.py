"""National data requirements, not claims of national data completeness.

The register lists minimum necessary information and independent checks. It is
intentionally independent of any optimization objective or political preference.
"""
from dataclasses import asdict, dataclass

@dataclass(frozen=True)
class Requirement:
    code: str
    sector: str
    data: str
    unit_examples: str
    update_frequency: str
    reporters: str
    cross_check: str
    sensitivity: str = "aggregate"
    critical: bool = True

REQUIREMENTS = [
    Requirement("population","social","population by age, geography and needs cohort","persons","monthly/annual","statistics offices, census, municipal registers","survey and migration reconciliation","restricted aggregate"),
    Requirement("household_needs","social","nutrition, housing, healthcare, mobility and access needs","units by service","weekly/monthly","local assemblies, independent surveys, service providers","representative surveys and independent grievances","restricted aggregate"),
    Requirement("unpaid_care","social","care hours and dependencies by cohort","hours","quarterly","time-use survey agencies","stratified time-use surveys","restricted aggregate"),
    Requirement("labour_supply","labour","hours, skills, credentials, availability and reasonable working-time limits","hours by skill","weekly","workplaces and labor institutes","payroll reconciliation, voluntary worker attestations","restricted aggregate"),
    Requirement("labour_safety","labour","hazard exposure, injuries, fatigue and conditions","incidents; hours","weekly/monthly","worker councils, safety inspectors","independent clinical and safety audits","restricted aggregate"),
    Requirement("activity_recipes","production","product outputs and physical inputs per technology and facility","physical quantity/unit","monthly/on-change","workplace engineers","meters, engineering audits and material bills"),
    Requirement("facility_capacity","production","usable production ceilings, bottlenecks and downtime","units/time","daily","production facilities","equipment condition measurements and production tests"),
    Requirement("capital_stock","production","equipment age, location, replacement and depreciation","units; operating hours","monthly","industrial inventories","site inspection and asset-register sampling"),
    Requirement("inventories","production","begin/end stocks, losses, quality and reserves","commodity units","daily","warehouses and enterprises","double-entry flows, physical stock counts"),
    Requirement("maintenance","production","required spare parts, replacement schedules and planned shutdowns","units; hours","weekly","plant engineering teams","breakdown and historical service records"),
    Requirement("quality","production","usable yield, defects, substitutions and service quality","units; %","daily/weekly","quality labs, workers, service users","blind sampling and downstream returns"),
    Requirement("electricity","energy","generation, imports, losses, demand, location and grid constraints","MWh; MW","5-min/hourly","generators, grid operators, substations","independent meters; generation=load+loss+net exports"),
    Requirement("fuels_heat","energy","fuel supplies, heat output, thermal efficiency and storage","kg; GJ","daily/hourly","refineries, fuel depots, heat operators","meter reconciliation; physical inventory"),
    Requirement("water","water","withdrawal, purification, distribution, quality, sewage and recharge","m3","daily","utilities, watersheds, laboratories","meter balance and independent sampling"),
    Requirement("agriculture","food","field area, inputs, harvest yields, storage spoilage and crop schedules","tonnes; hectares","weekly/seasonal","farms, cooperatives, agriculture ministry","remote sensing, crop cutting, weighing"),
    Requirement("nutrition","food","food composition, nutrition adequacy and distribution","nutrients; kg","monthly","public health, cooperatives, nutrition surveys","representative dietary survey and lab tests","restricted aggregate"),
    Requirement("housing","housing","habitable stock, suitability, repairs, new construction, land and occupancy","dwellings; m2","monthly","municipalities, housing boards, builders","sampled inspections and resident verification","restricted aggregate"),
    Requirement("healthcare","health","treatment capacity, medical equipment, staffing and waiting-time distributions","beds; visits; hours","daily/weekly","providers and public health agencies","independent clinical outcome audits","restricted aggregate"),
    Requirement("education","education","school capacity, accessible services, equipment and skills training","seats; hours","monthly/term","educational institutes, learner councils","surveys and inspected access","restricted aggregate"),
    Requirement("transport","transport","road, rail and marine capacities, schedules, congestion and maintenance","tonne-km; passenger-km","hourly/daily","operators, traffic agencies, depots","weighbridges, gauges and operator logs"),
    Requirement("logistics","logistics","commodity routes, vehicle availability, delivery times, spoilage and handling","tonnes; km; hours","daily","logistics coops, warehouses","shipment dispatch/receipt matching"),
    Requirement("communications","infrastructure","connectivity, redundancy, outages and communication capacity","bandwidth; uptime","daily","network operators and inspectors","independent uptime probes"),
    Requirement("ecology","ecology","emissions, energy flows, air, biodiversity, soil and restoration stocks","kgCO2e; hectares","weekly/annual","environment agencies and scientific institutes","independent calibrated environmental monitors"),
    Requirement("resource_limits","ecology","available nonrenewables, sustainable harvest, watershed and ecosystem boundaries","resource-specific","seasonal/annual","scientific institutions and local stewards","uncertainty review and independent fieldwork"),
    Requirement("imports_exports","external","imports, exports, foreign inputs, transit routes and import dependence","physical units; currencies","daily/monthly","customs, ports, trade bodies","customs and independent partner declarations"),
    Requirement("finance_transitional","transition","legacy monetary obligations, debt, external exchange and replacement financing","currencies","monthly","treasury, statistical agencies","independent reconciled public accounts"),
    Requirement("regional_equity","governance","spatial deprivation, accessibility, allocation outcomes and grievance resolution","need-satisfaction %","monthly","local councils, audits, population samples","independent representative audit and appeal","restricted aggregate"),
    Requirement("reserves_crises","resilience","critical emergency stocks, redundancy, supply-chain failures and recovery time","physical units; days","daily","emergency managers and workplaces","independent random spot checks"),
]
# Physical reports are scoped to well-defined quantities, not arbitrary user-provided keys.
METRICS = {
    "electricity_generated": ("kWh","electricity","flow"),
    "electricity_consumed": ("kWh","electricity","flow"),
    "electricity_grid_losses": ("kWh","electricity","flow"),
    "fuel_used": ("kg","fuels_heat","flow"),
    "water_delivered": ("m3","water","flow"),
    "water_withdrawn": ("m3","water","flow"),
    "harvest_output": ("kg","agriculture","flow"),
    "food_distributed": ("kg","nutrition","flow"),
    "inventory_end": ("kg","inventories","stock"),
    "equipment_capacity": ("unit/day","facility_capacity","rate"),
    "transport_freight": ("tonne-km","transport","flow"),
    "clinical_bed_days": ("bed-day","healthcare","flow"),
    "labor_worked": ("hour","labour_supply","flow"),
    "emissions_co2e": ("kgCO2e","ecology","flow"),
    "housing_habitable": ("dwelling","housing","stock"),
}

def inventory():
    return [asdict(r) for r in REQUIREMENTS]

def readiness():
    # Explicitly fail closed until independently audited, representative
    # sector datasets and entire interlocking input-output accounts exist.
    return {
        "national_planning_ready": False,
        "production_control_authorized": False,
        "required_information_domains":len(REQUIREMENTS),
        "independently_calibrated_domains":0,
        "missing_domains":[r.code for r in REQUIREMENTS],
        "note":"Pilot acquisition endpoints and public aggregate time series cannot establish full national data coverage.",
        "evidence_required":[
            "registered origin and legal basis","physical stock/flow and unit reconciliation",
            "independent field sampling","geographic and demographic representativeness",
            "uncertainty calibration and historical backtests","reviewable democratic needs priorities",
            "secure multi-institution reporting","independent security and human-rights assessment"
        ],
    }
