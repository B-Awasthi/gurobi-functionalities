import gurobipy as gp
from gurobipy import GRB

# product data
products, price = gp.multidict({"table": 80, "chair": 45})

# resources data
resources, availability = gp.multidict({"mahogany": 400, "labour": 450})

# rescources required by each product (bills of material)
bom = {
    ("mahogany", "chair"): 5,
    ("mahogany", "table"): 20,
    ("labour", "chair"): 10,
    ("labour", "table"): 15,
}

model = gp.Model("furniture_qcp")

make = model.addVars(products, name="make", vtype=GRB.CONTINUOUS)

res = model.addConstrs(
    gp.quicksum(bom[r, p] * make[p] for p in products) <= availability[r]
    for r in resources
)

objective_function = gp.quicksum(make[p] * price[p] for p in products)

model.setObjective(objective_function, sense=GRB.MAXIMIZE)

model.optimize()

# sensitivity report

# Value in the current solution.
for v in model.getVars():
    if abs(v.X) > 0.001:
        print(v.varName, v.X)

# Reduced cost of a variable
for v in model.getVars():
    print(v.varName, v.RC)

# Linear objective coefficient
for v in model.getVars():
    print(v.varName, v.obj)

# Objective coefficient sensitivity information
for v in model.getVars():
    print(
        v.varName, v.SAObjUp
    )  # largest objective coefficient value at which the current optimal basis would remain optimal
    print(
        v.varName, v.SAObjLow
    )  # smallest objective coefficient value at which the current optimal basis would remain optimal

# Slack in the current solution
for c in res:
    print(c, res[c].slack)

# Dual value (also known as the shadow price)
for c in res:
    print(c, res[c].pi)

# Right-hand side value.
for c in res:
    print(c, res[c].RHS)

# Right-hand side value.
for c in res:
    print(c, res[c].SARHSUp)
    print(c, res[c].SARHSLow)
