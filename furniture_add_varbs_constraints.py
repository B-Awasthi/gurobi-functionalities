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

make = model.addVars(products, name="make", obj=list(price.values()), vtype=GRB.INTEGER)

res = model.addConstrs(
    gp.quicksum(bom[r, p] * make[p] for p in products) <= availability[r]
    for r in resources
)


# =============================================================================
# change coefficient of the constraint and the RHS
# =============================================================================

add_prod = "bed"
make[add_prod] = model.addVar(
    obj=90, vtype=GRB.INTEGER, column=gp.Column([15, 18], res.values()), name="make[bed]"
)

# =============================================================================


model.ModelSense = GRB.MAXIMIZE
model.optimize()

# display solution
for v in model.getVars():
    if abs(v.X) > 0.001:
        print(v.varName, v.X)

model.write("model.lp")
