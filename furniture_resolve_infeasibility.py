import gurobipy as gp
from gurobipy import GRB

# product data
products, price = gp.multidict({"table": 80, "chair": 45})

# resources data
resources, availability = gp.multidict({"mahogany": 9, "labour": 9})  # 400, 450

# rescources required by each product (bills of material)
bom = {
    ("mahogany", "chair"): 5,
    ("mahogany", "table"): 20,
    ("labour", "chair"): 10,
    ("labour", "table"): 15,
}

model = gp.Model("furniture")

make = model.addVars(
    products, name="make", obj=list(price.values()), vtype=GRB.INTEGER, lb=1
)

res = model.addConstrs(
    gp.quicksum(bom[r, p] * make[p] for p in products) <= availability[r]
    for r in resources
)


model.ModelSense = GRB.MAXIMIZE
model.optimize()

# =============================================================================
# resolve infeasibility
# =============================================================================

model.computeIIS()

# Print out the IIS constraints and variables
print("\nThe following constraints and variables are in the IIS:")
for c in model.getConstrs():
    if c.IISConstr:
        print(f"\t{c.constrname}: {model.getRow(c)} {c.Sense} {c.RHS}")

for v in model.getVars():
    if v.IISLB:
        print(f"\t{v.varname} ≥ {v.LB}")
    if v.IISUB:
        print(f"\t{v.varname} ≤ {v.UB}")

model.write("model_infeasible.ilp")

# resolve infeasibility - 1
if model.status == GRB.INFEASIBLE:
    # model.feasRelaxS(1, True, False, True)

    ubpen = [0.1] * model.numVars
    model.feasRelax(
        relaxobjtype=2,
        minrelax=False,
        vars=model.getVars(),
        lbpen=None,
        ubpen=ubpen,
        constrs=[res["mahogany"], res["labour"]],
        rhspen=[1, 1],
    )
    model.optimize()

# resolve infeasibility - 2
if model.status == GRB.INFEASIBLE:
    model.feasRelaxS(relaxobjtype=2, minrelax=False, vrelax=True, crelax=True)
    model.optimize()

# =============================================================================

# display solution
for v in model.getVars():
    if abs(v.X) > 0.001:
        print(v.varName, v.X)

model.write("model.lp")
