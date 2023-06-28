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

objective_function = make.prod(price)

model.setObjective(objective_function, sense=GRB.MAXIMIZE)

model.optimize()

# =============================================================================
# change coefficient of the constraint and the RHS
# =============================================================================

model.update()

for i in resources:
    print(i + "_RHS = => " + str(res[i].getAttr("RHS")))

# change RHS:
for i in resources:
    res[i].setAttr("RHS", 500)

# check:
model.update()
for i in resources:
    print(i + "_RHS = => " + str(res[i].getAttr("RHS")))

# current objective coeff for variables:
for p in products:
    print(p + " => " + str(make[p].getAttr("Obj")))

# change coefficient for variables for each constraint
for p in products:
    for i in resources:
        model.chgCoeff(res[i], make[p], 50)

# set objective coeff for variables:
model.update()
for p in products:
    make[p].setAttr("Obj", 50)

# check:
model.update()
for p in products:
    print(p + " => " + str(make[p].getAttr("Obj")))


for p in products:
    cons = model.getCol(make[p])
    for i in range(cons.size()):
        print(p + "constraint_" + str(i) + " => " + str(cons.getCoeff(i)))

# =============================================================================

model.optimize()

# display solution
for v in model.getVars():
    if abs(v.X) > 0.001:
        print(v.varName, v.X)
