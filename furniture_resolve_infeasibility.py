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
model.write("model.ilp")

if model.status == GRB.INFEASIBLE:
    # model.feasRelaxS(1, True, False, True)

    ubpen = [0.1] * model.numVars
    model.feasRelax(
        relaxobjtype=1,
        minrelax=False,
        vars=model.getVars(),
        lbpen=None,
        ubpen=ubpen,
        constrs=[res["mahogany"], res["labour"]],
        rhspen=[1, 1],
    )
    model.optimize()

# =============================================================================


# display solution
for v in model.getVars():
    if abs(v.X) > 0.001:
        print(v.varName, v.X)

model.write("model.lp")
