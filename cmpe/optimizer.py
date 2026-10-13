"""Auditable linear programming, with needs coverage lexicographically prior to resources."""
import numpy as np
from scipy.optimize import linprog
from .schema import Economy

def optimize(economy: Economy) -> dict:
    goods = list(economy.units)
    activities = economy.activities
    n = len(activities)
    net = np.array([[a.outputs.get(g, 0.0)-a.inputs.get(g, 0.0)
                     for a in activities] for g in goods],dtype=float)
    needs = np.array([economy.essential_needs[g] for g in goods],dtype=float)
    labor = np.array([a.labor_hours for a in activities],dtype=float)
    carbon = np.array([a.emissions_kg for a in activities],dtype=float)
    caps = [(0.0,a.capacity) for a in activities] + [(0.0,1.0)]
    # net production must cover an equal minimum fraction of every essential need.
    lhs = np.column_stack((-net, needs))
    A = np.vstack((lhs, np.append(labor,0),np.append(carbon,0)))
    b = np.concatenate((np.zeros(len(goods)),[economy.labor_budget_hours,economy.emissions_budget_kg]))
    c = np.append(np.zeros(n),-1.0)
    first = linprog(c,A_ub=A,b_ub=b,bounds=caps,method="highs")
    if not first.success:
        raise ValueError("no feasible physical plan: "+first.message)
    coverage = float(np.clip(first.x[-1],0,1))
    # Minimum labor and emissions among plans attaining optimal guaranteed coverage.
    second_c = np.append(labor+carbon*1e-6,0.0)
    second_bounds = caps[:-1]+[(max(0,coverage-1e-8),min(1,coverage+1e-8))]
    second = linprog(second_c,A_ub=A,b_ub=b,bounds=second_bounds,method="highs")
    if not second.success:
        raise ValueError("secondary optimization failed: "+second.message)
    x = second.x[:n]
    output = net @ x
    residual = output-needs*coverage
    if (residual < -1e-5).any() or labor @ x>economy.labor_budget_hours+1e-5 or carbon @ x>economy.emissions_budget_kg+1e-5:
        raise RuntimeError("post-solve physical feasibility failed")
    return {
        "mode":"advisory-simulation-only",
        "coverage_fraction":coverage,
        "activities":{a.name:float(round(x[i],8)) for i,a in enumerate(activities)},
        "net_available":{g:float(round(output[i],8)) for i,g in enumerate(goods)},
        "essential_needs":dict(economy.essential_needs),
        "labor_used_hours":float(round(labor @ x,8)),
        "emissions_used_kg":float(round(carbon @ x,8)),
        "solver":"scipy.optimize.linprog/highs",
        "max_balance_violation":float(max(0.0,-residual.min())),
    }
