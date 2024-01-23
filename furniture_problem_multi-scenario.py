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

model = gp.Model("furniture_multi-scenario")

make = model.addVars(products, name="make")

res = model.addConstrs(
    gp.quicksum(bom[r, p] * make[p] for p in products) <= availability[r]
    for r in resources
)

objective_function = make.prod(price)

model.setObjective(objective_function, sense=GRB.MAXIMIZE)

# =============================================================================
# generate different scenarios
# =============================================================================

# total number of scenarios
model.NumScenarios = 4

# scenarion 0 : base scenario
model.Params.ScenarioNumber = 0
model.ScenNName = "Base model"

# scenario 1 : increase availability by 10%
model.Params.ScenarioNumber = 1
model.ScenNName = "Increase availability"
for r in resources:
    res[r].ScenNRhs = availability[r] * 1.1

# scenario 2 : increase objective coeff by 10%
model.Params.ScenarioNumber = 2
model.ScenNName = "Increase objective function coefficients"
for p in products:
    make[p].ScenNObj = price[p] * 1.3

# scenario 3 : combine scenarios 1 and 2
model.Params.ScenarioNumber = 3
model.ScenNName = "Combine scenario 1 and 2"
for r in resources:
    res[r].ScenNRhs = availability[r] * 1.1
for p in products:
    make[p].ScenNObj = price[p] * 1.3

# Save model
model.write("multiscenario.lp")

# Solve multi-scenario model
model.optimize()

# Print solution for each scenario
for s in range(model.NumScenarios):
    model.Params.ScenarioNumber = s
    print("scenario number = " + str(s))
    for v in model.getVars():
        if abs(v.ScenNX) > 0.001:
            print(v.varName, v.ScenNX)
    print("-" * 50)


# display solution
# for v in model.getVars():
#     if abs(v.X) > 0.001:
#         print(v.varName, v.X)
