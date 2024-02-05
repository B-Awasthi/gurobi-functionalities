import math
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

# add non linear constraints

# ----------------------------------------------------- #
# ----------------------------------------------------- #
# PWL constraint approach
# ----------------------------------------------------- #
# exp(table / 10) + 4 * sqrt(chair) <= 25
table_10 = model.addVar(name="table_div_10")
model.addConstr(table_10 == make["table"] / 10)
exp_table_10 = model.addVar(name="exp_table_10")

sqrt_chair = model.addVar(name="sqrt_chair")

model.addConstr(exp_table_10 + (4 * sqrt_chair) <= 25)

xpts = []
ypts = []
upts = []
vpts = []

intv = 0.5
xmax = 2
t = 0
while t < xmax + intv:
    xpts.append(t)
    upts.append(math.exp(t))
    t += intv


ymax = 10
t = 0.0
while t < ymax + intv:
    ypts.append(t)
    vpts.append(math.sqrt(t))
    t += intv

gc1 = model.addGenConstrPWL(table_10, exp_table_10, xpts, upts, "gc1")
gc2 = model.addGenConstrPWL(make["chair"], sqrt_chair, ypts, vpts, "gc2")

objective_function = make.prod(price)

model.setObjective(objective_function, sense=GRB.MAXIMIZE)

model.optimize()

# display solution
for v in model.getVars():
    if abs(v.X) > 0.001:
        print(v.varName, v.X)

# ----------------------------------------------------- #
# ----------------------------------------------------- #
# General function constraint approach with auto PWL
#             translation by Gurobi
# ----------------------------------------------------- #

model.reset()
model.remove(gc1)
model.remove(gc2)

gcf1 = model.addGenConstrExp(table_10, exp_table_10, name="gcf1")
gcf2 = model.addGenConstrPow(make["chair"], sqrt_chair, 0.5, name="gcf2")

model.Params.FuncPieces = 1
model.Params.FuncPieceLength = 0.1

model.optimize()

# display solution
for v in model.getVars():
    if abs(v.X) > 0.001:
        print(v.varName, v.X)
