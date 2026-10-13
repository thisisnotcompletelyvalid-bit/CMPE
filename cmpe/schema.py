"""Strict, explicitly unit-bearing technology and needs contract."""
from math import isfinite
from pydantic import BaseModel, ConfigDict, Field, model_validator

def finite_nonnegative(v):
    return isfinite(v) and v >= 0

class Activity(BaseModel):
    model_config = ConfigDict(extra="forbid")
    name: str = Field(min_length=1, max_length=96)
    inputs: dict[str, float] = Field(default_factory=dict)
    outputs: dict[str, float]
    labor_hours: float = Field(ge=0)
    emissions_kg: float = Field(ge=0)
    capacity: float = Field(ge=0)

class Economy(BaseModel):
    model_config = ConfigDict(extra="forbid")
    name: str = Field(min_length=1, max_length=120)
    units: dict[str, str] = Field(min_length=1, max_length=80)
    activities: list[Activity] = Field(min_length=1, max_length=250)
    essential_needs: dict[str, float]
    labor_budget_hours: float = Field(gt=0)
    emissions_budget_kg: float = Field(ge=0)
    provenance: str = Field(min_length=8, max_length=1000)

    @model_validator(mode="after")
    def consistency(self):
        goods = set(self.units)
        if not goods or len(self.activities) > 250 or len(set(a.name for a in self.activities)) != len(self.activities):
            raise ValueError("duplicate activities or invalid goods")
        for name, unit in self.units.items():
            if not name or len(name)>80 or not unit or len(unit)>50:
                raise ValueError("invalid commodity or unit")
        if set(self.essential_needs) != goods:
            raise ValueError("essential_needs must specify exactly the declared goods")
        values = list(self.essential_needs.values()) + [self.labor_budget_hours,self.emissions_budget_kg]
        for a in self.activities:
            if not set(a.inputs).issubset(goods) or not set(a.outputs).issubset(goods):
                raise ValueError("undeclared input/output commodity")
            if not a.outputs or not any(x > 0 for x in a.outputs.values()):
                raise ValueError("activity must have a strictly positive output")
            values.extend([a.labor_hours,a.emissions_kg,a.capacity])
            values.extend(a.inputs.values())
            values.extend(a.outputs.values())
        if not all(finite_nonnegative(float(v)) for v in values):
            raise ValueError("nonfinite or negative coefficient")
        return self
