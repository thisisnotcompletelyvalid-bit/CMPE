from cmpe.capacity import estimate
from cmpe.schema import Economy
from cmpe.optimizer import optimize

def test_capacity_estimating_units():
    x=estimate(reporters=10000,records_per_reporter_daily=1000,bytes_per_record=1000,
               retention_years=1,storage_copies=1)
    assert x["daily_records"]==10_000_000
    assert abs(x["raw_annual_terabytes"]-3.65)<0.01
    assert x["national_readiness"] is False

def test_sparse_plan_with_many_alternative_technologies():
    data={
        "name":"Synthetic sparse research stress fixture",
        "units":{"energy":"kWh","food":"kg"},
        "activities":[
            {"name":"energy"+str(i),"inputs":{},"outputs":{"energy":1},"labor_hours":0.1,
             "emissions_kg":0.02,"capacity":2} for i in range(450)
        ] + [{"name":"food-factory","inputs":{"energy":0.2},"outputs":{"food":1},
              "labor_hours":0.1,"emissions_kg":0.02,"capacity":50}],
        "essential_needs":{"energy":50,"food":40},
        "labor_budget_hours":400,
        "emissions_budget_kg":100,
        "provenance":"Explicitly synthetic sparse algorithm research test",
    }
    s=Economy.model_validate(data)
    out=optimize(s)
    assert out["coverage_fraction"]>0.9999
    assert out["matrix_nonzeros"]<=1000
    assert out["max_balance_violation"]<1e-5
