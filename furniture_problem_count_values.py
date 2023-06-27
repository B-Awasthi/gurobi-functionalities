import gurobipy as gp
from gurobipy import GRB

# product data
products, price = gp.multidict({"table": 95, "chair": 45, "bed": 100, "study_table": 75})

# resources data
resources, availability = gp.multidict({"mahogany": 1000, "labour": 1000})

# rescources required by each product (bills of material)
bom = {
    ("mahogany", "chair"): 5,
    ("mahogany", "table"): 20,
    ("mahogany", "bed"): 20,
    ("mahogany", "study_table"): 15,
    ("labour", "chair"): 10,
    ("labour", "table"): 15,
    ("labour", "bed"): 15,
    ("labour", "study_table"): 15,
}

model = gp.Model("furniture")

make = model.addVars(products, name="make", lb=10, ub=30)

res = model.addConstrs(
    gp.quicksum(bom[r, p] * make[p] for p in products) <= availability[r]
    for r in resources
)

# =============================================================================
# number of distinct values for products should be <= 1
# =============================================================================

vals = list(range(10, 31))
counter = model.addVars(products, range(10, 31), vtype=GRB.BINARY)
sum_counter = model.addVars(range(10, 31), vtype=GRB.INTEGER)

for p in products:
    model.addConstr(
        make[p] == gp.quicksum(a * b for a, b in zip(counter.select(p, "*"), vals))
    )

model.addConstrs(sum_counter[t] == counter.sum("*", t) for t in vals)

model.addSOS(GRB.SOS_TYPE1, [sum_counter[t] for t in vals])

# =============================================================================

objective_function = make.prod(price)

model.setObjective(objective_function, sense=GRB.MAXIMIZE)

model.optimize()

# names_to_retrieve = [varb for varb in model.getVars() if "make" in varb.VarName]
names_to_retrieve = [f"make[{p}]" for p in products]
variables = [model.getVarByName(name) for name in names_to_retrieve]

# display solution
for v in variables:
    if abs(v.X) > 0.001:
        print(v.varName, v.X)
