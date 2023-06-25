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
# maximize exp(table) + exp(chair)
# =============================================================================

make_exp = model.addVars(products, vtype=GRB.CONTINUOUS, name="make_exp")

for p in products:
    model.addGenConstrExp(make[p], make_exp[p])

# =============================================================================

objective_function = gp.quicksum(make_exp)

model.setObjective(objective_function, sense=GRB.MAXIMIZE)

model.optimize()

# display solution
for v in make:
    if abs(make[v].X) > 0.001:
        print(make[v].varName, make[v].X)
