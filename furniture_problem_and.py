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
# number of table <= 9 and number of chair >= 21
# =============================================================================

bool_table = model.addVar(vtype=GRB.BINARY)
bool_chair = model.addVar(vtype=GRB.BINARY)

model.addGenConstrIndicator(bool_table, 1, make["table"] <= 9)
model.addGenConstrIndicator(bool_chair, 1, make["chair"] >= 21)

res_var = model.addVar(vtype=GRB.BINARY, lb=1, ub=1)
model.addGenConstrAnd(res_var, [bool_table, bool_chair])

# =============================================================================

objective_function = make.prod(price)

model.setObjective(objective_function, sense=GRB.MAXIMIZE)

model.optimize()

# display solution
for v in make:
    if abs(make[v].X) > 0.001:
        print(make[v].varName, make[v].X)
