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
# if both table and chair are produced then a penalty will be imposed
# =============================================================================

number_of_products_produced = model.addVar(vtype=GRB.INTEGER, ub=2)

is_table_produced = model.addVar(vtype=GRB.BINARY)
is_chair_produced = model.addVar(vtype=GRB.BINARY)

model.addGenConstrIndicator(is_table_produced, 0, make["table"] <= 0)
model.addGenConstrIndicator(is_chair_produced, 0, make["chair"] <= 0)

model.addConstr(number_of_products_produced == is_table_produced + is_chair_produced)

# =============================================================================

objective_function = make.prod(price)
objective_function += -number_of_products_produced * 500

model.setObjective(objective_function, sense=GRB.MAXIMIZE)

model.optimize()

# display solution
for v in model.getVars():
    if abs(v.X) > 0.001:
        print(v.varName, v.X)

model.write("model.lp")
