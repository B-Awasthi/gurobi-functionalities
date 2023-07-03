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

make = model.addVars(products, vtype=GRB.INTEGER, name="make")

res = model.addConstrs(
    gp.quicksum(bom[r, p] * make[p] for p in products) <= availability[r]
    for r in resources
)

# =============================================================================
# make a clone of the original model
# =============================================================================

objective_function = make.prod(price)
model.setObjective(objective_function, sense=GRB.MAXIMIZE)

model.optimize()

model.update()
model_copy = model.copy()
model_equal = model

model.setAttr("LB", make["table"], 5)
model.setAttr("UB", make["table"], 5)

model_copy.optimize()
model_equal.optimize()

# display solution : original model
for v in model_copy.getVars():
    if abs(v.X) > 0.001:
        print(v.varName, v.X)


# display solution : model post we add equal constraints (model_equal)
for v in model_equal.getVars():
    if abs(v.X) > 0.001:
        print(v.varName, v.X)

# =============================================================================
