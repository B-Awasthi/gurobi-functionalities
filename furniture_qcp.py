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

make = model.addVars(products, name="make")

res = model.addConstrs(
    gp.quicksum(bom[r, p] * make[p] for p in products) <= availability[r]
    for r in resources
)

# make['table'] ** 2 + make['chair'] ** 2 <= 1000
model.addQConstr(make["table"] ** 2 + make["chair"] ** 2 <= 1000, "qc")

objective_function = gp.quicksum(make[p] * price[p] for p in products)

model.setObjective(objective_function, sense=GRB.MAXIMIZE)

# model.params.NonConvex = 2

model.optimize()

# display solution
for v in model.getVars():
    if abs(v.X) > 0.001:
        print(v.varName, v.X)
