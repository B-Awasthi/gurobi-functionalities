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
# number of tables produced should be either <= 10 or >= 20
# =============================================================================

delta_le_10 = model.addVar(vtype=GRB.BINARY)
delta_ge_20 = model.addVar(vtype=GRB.BINARY)
delta_or = model.addVar(vtype=GRB.BINARY, lb=1, ub=1)

model.addGenConstrIndicator(delta_le_10, 1, make["table"] <= 10)
model.addGenConstrIndicator(delta_ge_20, 1, make["table"] >= 20)

model.addGenConstrOr(delta_or, [delta_le_10, delta_ge_20])
# model.addConstr(delta_le_10 + delta_ge_20 >= 1)

# =============================================================================

objective_function = make.prod(price)

model.setObjective(objective_function, sense=GRB.MAXIMIZE)

model.optimize()

# display solution
for v in model.getVars():
    if abs(v.X) > 0.001:
        print(v.varName, v.X)
