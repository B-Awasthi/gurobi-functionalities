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

make = model.addVars(
    products, name="make", obj=list(price.values()), vtype=GRB.INTEGER, lb=1
)

res = model.addConstrs(
    gp.quicksum(bom[r, p] * make[p] for p in products) <= availability[r]
    for r in resources
)


# =============================================================================
# if number of tables >= 10 then number of chairs >= 25
# =============================================================================

# num_tables >= 10 ==> delta == 1
# OR delta == 0 ==> num_tables <= 9
# delta == 1 ==> num_chairs >= 25

delta = model.addVar(vtype=GRB.BINARY)
model.addGenConstrIndicator(delta, 0, make["table"] <= 9)
model.addGenConstrIndicator(delta, 1, make["chair"] >= 25)

# =============================================================================

model.ModelSense = GRB.MAXIMIZE
model.optimize()

# display solution
for v in model.getVars():
    if abs(v.X) > 0.001:
        print(v.varName, v.X)

model.write("model.lp")
