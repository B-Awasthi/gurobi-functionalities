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

model = gp.Model("furniture")

make = model.addVars(products, name="make", vtype=GRB.INTEGER)

res = model.addConstrs(
    gp.quicksum(bom[r, p] * make[p] for p in products) <= availability[r]
    for r in resources
)

# =============================================================================
# warm start
# =============================================================================

# Start attribute

model.NumStart = 2
model.update()

# iterate over all MIP starts
for s in range(model.NumStart):
    model.params.StartNumber = s
    if s == 0:
        model.setAttr("Start", make["chair"], 22)
    else:
        model.setAttr("Start", make["table"], 14)
        model.setAttr("Start", make["chair"], 24)


# Variable Hints
model.setAttr("VarHintVal", make["table"], 12)
model.setAttr("VarHintVal", make["chair"], 22)

# =============================================================================

objective_function = make.prod(price)

model.setObjective(objective_function, sense=GRB.MAXIMIZE)

model.optimize()

# display solution
for v in model.getVars():
    if abs(v.X) > 0.001:
        print(v.varName, v.X)
