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


# =============================================================================
# number of tables and chairs can take values only in ranges [(1, 8), (10, 12), (15, 20), (25, 30)]
# =============================================================================

ranges = [(1, 8), (10, 12), (15, 20), (25, 30)]
make_bool_varbs = model.addVars(products, range(len(ranges)), vtype=GRB.BINARY)

for p in products:
    for ind, ij in enumerate(ranges):
        model.addGenConstrIndicator(make_bool_varbs[p, ind], 1, make[p] >= ij[0])
        model.addGenConstrIndicator(make_bool_varbs[p, ind], 1, make[p] <= ij[1])

for p in products:
    model.addConstr(make_bool_varbs.sum(p, "*") == 1)

# =============================================================================

res = model.addConstrs(
    gp.quicksum(bom[r, p] * make[p] for p in products) <= availability[r]
    for r in resources
)

objective_function = make.prod(price)

model.setObjective(objective_function, sense=GRB.MAXIMIZE)

model.optimize()

# display solution
for v in model.getVars():
    if abs(v.X) > 0.001:
        print(v.varName, v.X)
