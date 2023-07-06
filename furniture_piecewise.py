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

make = model.addVars(products, name="make")

res = model.addConstrs(
    gp.quicksum(bom[r, p] * make[p] for p in products) <= availability[r]
    for r in resources
)


# =============================================================================
# table : 0 - 5 : $80 ; 5 - 10 : 10% cheaper ; > 10  : 20% cheaper
# chair : 0 - 10 : $45 ; 10 - 20 : 10% cheaper ; > 20 : 20% cheaper
# =============================================================================

num_tbl = range(100)
num_chair = range(100)

revenue_table = []
for i in num_tbl:
    if i == 0:
        revenue_table.append(0)
    elif i <= 5:
        revenue_table.append(80 * i)
    elif (i > 5) and (i <= 10):
        revenue_table.append(80 * i * 0.90)
    else:
        revenue_table.append(80 * i * 0.80)

revenue_chair = []
for i in num_tbl:
    if i == 0:
        revenue_chair.append(0)
    elif i <= 10:
        revenue_chair.append(45 * i)
    elif (i > 5) and (i <= 10):
        revenue_chair.append(45 * i * 0.90)
    else:
        revenue_chair.append(45 * i * 0.80)


model.setPWLObj(make["table"], num_tbl, revenue_table)
model.setPWLObj(make["chair"], num_chair, revenue_chair)

model.ModelSense = GRB.MAXIMIZE

model.optimize()

# display solution
for v in model.getVars():
    if abs(v.X) > 0.001:
        print(v.varName, v.X)
