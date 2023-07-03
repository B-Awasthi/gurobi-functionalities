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
# both table and chair should be >= 10 AND atleast one of them should be 18
# =============================================================================

# both table and chair should be >= 10
model.addConstrs(make[p] >= 10 for p in products)

# atleast one of table and chair them should be 18
bool_table = model.addVar(vtype=GRB.BINARY)
bool_chair = model.addVar(vtype=GRB.BINARY)

model.addGenConstrIndicator(bool_table, 1, make["table"] == 18)
model.addGenConstrIndicator(bool_chair, 1, make["chair"] == 18)

model.addConstr(bool_table + bool_chair >= 1)

# =============================================================================

objective_function = make.prod(price)

model.setObjective(objective_function, sense=GRB.MAXIMIZE)

model.optimize()

# display solution
for v in make:
    if abs(make[v].X) > 0.001:
        print(make[v].varName, make[v].X)
