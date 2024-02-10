import gurobipy as gp
from gurobipy import GRB

# https://www.gurobi.com/documentation/current/refman/cb_codes.html
# https://www.gurobi.com/documentation/current/examples/cb_py.html

model = gp.read("/Library/gurobi1001/macos_universal2/examples/data/glass4.mps")


# callback 1


# MIP optimizer to run for 10 seconds before quitting,
# but we don't want it to terminate before it finds a feasible solution
def mycallback(model, where):
    if where == GRB.Callback.MIP:
        time = model.cbGet(GRB.Callback.RUNTIME)
        best = model.cbGet(GRB.Callback.MIP_OBJBST)
        if time > 10 and best < GRB.INFINITY:
            model.terminate()


model.optimize(mycallback)


# callback 2

# The TimeLimit parameter forces the optimization to terminate after 100 seconds.
# In addition, when the MIP gap is smaller than 50% and at least 5 seconds have passed,
# the optimization will terminate.

softlimit = 5
hardlimit = 30


def softtime(model, where):
    if where == GRB.Callback.MIP:
        runtime = model.cbGet(GRB.Callback.RUNTIME)
        objbst = model.cbGet(GRB.Callback.MIP_OBJBST)
        objbnd = model.cbGet(GRB.Callback.MIP_OBJBND)
        gap = abs((objbst - objbnd) / objbst)

        if runtime > softlimit and gap < 0.5:
            model.terminate()


model.setParam("TimeLimit", hardlimit)
model.optimize(softtime)


# callback 3


class CallbackData:
    def __init__(self, modelvars):
        self.modelvars = modelvars
        self.lastiter = -GRB.INFINITY
        self.lastnode = -GRB.INFINITY


cbdata = CallbackData(model.getVars())


def mycallback(model, where):
    if where == GRB.Callback.MIPSOL:
        nodecnt = model.cbGet(GRB.Callback.MIPSOL_NODCNT)
        obj = model.cbGet(GRB.Callback.MIPSOL_OBJ)
        solcnt = model.cbGet(GRB.Callback.MIPSOL_SOLCNT)
        x = model.cbGetSolution(cbdata.modelvars)
        print(
            f"**** New solution at node {nodecnt:.0f}, obj {obj:g}, "
            f"sol {solcnt:.0f}, x[0] = {x[0]:g} ****"
        )
        time = model.cbGet(GRB.Callback.RUNTIME)
        best = model.cbGet(GRB.Callback.MIPSOL_OBJBST)
        if time > 10 and best < GRB.INFINITY:
            model.terminate()


model.optimize(mycallback)
