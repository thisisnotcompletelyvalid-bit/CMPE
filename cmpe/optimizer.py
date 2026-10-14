"""Sparse linear planning under physical capacity, labor and emissions constraints.

Advisory-only. This is NOT a complete dynamic national input-output solver.
"""
import numpy as np
from scipy import sparse
from scipy.optimize import linprog
from .schema import Economy

def optimize(economy: Economy) -> dict:
    goods=list(economy.units)
    sectors=economy.activities
    index={g:i for i,g in enumerate(goods)}
    rows,cols,values=[],[],[]
    for j,a in enumerate(sectors):
        for g,qty in a.outputs.items():
            if qty:rows.append(index[g]);cols.append(j);values.append(qty)
        for g,qty in a.inputs.items():
            if qty:rows.append(index[g]);cols.append(j);values.append(-qty)
    net=sparse.coo_matrix((values,(rows,cols)),shape=(len(goods),len(sectors))).tocsr()
    net.sum_duplicates()
    needs=np.array([economy.essential_needs[g] for g in goods],dtype=float)
    labor=np.fromiter((a.labor_hours for a in sectors),dtype=float)
    carbon=np.fromiter((a.emissions_kg for a in sectors),dtype=float)
    n=len(sectors)
    bounds=[(0.0,a.capacity) for a in sectors]+[(0.0,1.0)]
    lhs=sparse.hstack((-net,sparse.csr_matrix(needs.reshape(-1,1))),format="csr")
    A=sparse.vstack((lhs,sparse.csr_matrix(np.r_[labor,0]),sparse.csr_matrix(np.r_[carbon,0])),format="csr")
    b=np.concatenate((np.zeros(len(goods)),[economy.labor_budget_hours,economy.emissions_budget_kg]))
    first=linprog(np.r_[np.zeros(n),-1.0],A_ub=A,b_ub=b,bounds=bounds,method="highs")
    if not first.success:raise ValueError("infeasible mathematical plan: "+first.message)
    coverage=float(np.clip(first.x[-1],0.0,1.0))
    second=linprog(np.r_[labor+1e-6*carbon,0],A_ub=A,b_ub=b,
                   bounds=bounds[:-1]+[(max(0,coverage-1e-8),min(1,coverage+1e-8))],
                   method="highs")
    if not second.success:raise ValueError("secondary optimizer failed: "+second.message)
    x=second.x[:n]
    output=np.asarray(net @ x).ravel()
    residual=output-needs*coverage
    if (residual<-1e-5).any() or labor@x>economy.labor_budget_hours+1e-5 or carbon@x>economy.emissions_budget_kg+1e-5:
        raise RuntimeError("independent physical balance/constraint verification failed")
    return {
        "mode":"advisory-simulation-only",
        "coverage_fraction":coverage,
        "activities":{a.name:float(round(x[i],8)) for i,a in enumerate(sectors)},
        "net_available":{g:float(round(output[i],8)) for i,g in enumerate(goods)},
        "essential_needs":dict(economy.essential_needs),
        "labor_used_hours":float(round(labor@x,8)),
        "emissions_used_kg":float(round(carbon@x,8)),
        "solver":"scipy.optimize.linprog/highs/sparse-csr",
        "matrix_nonzeros":int(net.nnz),
        "max_balance_violation":float(max(0.0,-residual.min())),
    }
