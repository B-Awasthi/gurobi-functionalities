import gurobipy as gp
from gurobipy import GRB

products, price = gp.multidict({"table": 80, "chair": 45})
resources, availability = gp.multidict({"mahogany": 400, "labour": 450})

bom = {
    ("mahogany", "chair"): 5,
    ("mahogany", "table"): 20,
    ("labour", "chair"): 10,
    ("labour", "table"): 15,
}

model = gp.Model("furniture")

make = model.addVars(products, name="make", obj=list(price.values()), vtype=GRB.INTEGER)

res = model.addConstrs(
    (
        gp.quicksum(bom[r, p] * make[p] for p in products) <= availability[r]
        for r in resources
    ),
    name="avail",
)

model.ModelSense = GRB.MAXIMIZE
model.optimize()

# Now, I make add another product to the formulation -

add_prod = "bed"
make[add_prod] = model.addVar(
    obj=90, vtype=GRB.INTEGER, column=gp.Column([15, 18], res.values()), name="make[bed]"
)

model.optimize()

# =============================================================================
#
# =============================================================================

model.update()

print(f"Obj: {model.getObjective()}")
for r in resources:
    print(f"{res[r].ConstrName}: {model.getRow(res[r])} {res[r].Sense} {res[r].RHS}")

obj = model.getObjective()
for i in range(obj.size()):
    print(f"{obj.getCoeff(i)} * {obj.getVar(i).VarName}")
