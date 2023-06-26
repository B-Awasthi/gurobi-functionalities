import gurobipy as gp
from gurobipy import GRB

# product data
products, price = gp.multidict({"table": 95, "chair": 45, "bed": 100})

# resources data
resources, availability = gp.multidict({"mahogany": 1000, "labour": 1000})

# rescources required by each product (bills of material)
bom = {
    ("mahogany", "chair"): 5,
    ("mahogany", "table"): 20,
    ("mahogany", "bed"): 20,
    ("labour", "chair"): 10,
    ("labour", "table"): 15,
    ("labour", "bed"): 15,
}

model = gp.Model("furniture")

make = model.addVars(products, name="make", lb=10)

res = model.addConstrs(
    gp.quicksum(bom[r, p] * make[p] for p in products) <= availability[r]
    for r in resources
)

objective_function = make.prod(price)

model.setObjective(objective_function, sense=GRB.MAXIMIZE)

model.optimize()

# display solution
for v in model.getVars():
    if abs(v.X) > 0.001:
        print(v.varName, v.X)
