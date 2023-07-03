import itertools
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

make = model.addVars(products, vtype=GRB.INTEGER, name="make", lb=10, ub=30)

res = model.addConstrs(
    gp.quicksum(bom[r, p] * make[p] for p in products) <= availability[r]
    for r in resources
)

# =============================================================================
# all products should have distinct values
# =============================================================================

combin = list(itertools.combinations(range(len(products)), 2))

# inspired from :
# https://stackoverflow.com/questions/50428510/how-to-express-the-not-equals-relation-in-linear-programming/50429421#50429421

big_M = 100
for i, j in combin:
    bin_var = model.addVar(vtype=GRB.BINARY)
    model.addConstr(make[products[i]] <= make[products[j]] - 1 + (big_M * bin_var))
    model.addConstr(make[products[i]] >= make[products[j]] + 1 - big_M * (1 - bin_var))

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
