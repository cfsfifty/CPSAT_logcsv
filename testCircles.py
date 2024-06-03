''' 
    05.2024, Christoph Fuenfzig
'''
from   SolverStatsCSV import SolverStatsCSV
from   ortools.sat.python import cp_model 

# CPSAT model
model = cp_model.CpModel()

num_circles_dim = 5
# use one-hundreth(1/100)
unit            = 100
# everything in unit
radius_circles  = 1*unit
size_area       = num_circles_dim*unit

def constraints_distance (dx, dy, r1, r2):
    sdx = model.NewIntVar(0, size_area*size_area, 'sdx_local')
    sdy = model.NewIntVar(0, size_area*size_area, 'sdy_local')
    model.AddMultiplicationEquality(sdx, [dx, dx])
    model.AddMultiplicationEquality(sdy, [dy, dy])
    model.Add(sdx + sdy >= r1*r1+r2*r2)


coordx  = []
coordy  = []
border  = [] # lower-right border circles
for j in range(num_circles_dim):
    for i in range(num_circles_dim):
        coordx.append(model.NewIntVar(0, size_area, 'x_%d_%d' % (i, j)))
        coordy.append(model.NewIntVar(0, size_area, 'y_%d_%d' % (i, j)))
        if i == num_circles_dim-1:
            border.append(coordx[-1])
border.extend(coordy[-num_circles_dim:])

for j in range(num_circles_dim):
    for i in range(num_circles_dim):
        if i == 0 and j == 0: # fix circle 0 to (0, 0)
            model.Add(coordx[j + i*num_circles_dim] == 0)
            model.Add(coordy[j + i*num_circles_dim] == 0)
        if i > 0 and j > 0:
            dx = model.NewIntVar(-size_area, size_area, 'dx_%d_%d' % (i, j))
            dy = model.NewIntVar(-size_area, size_area, 'dy_%d_%d' % (i, j))
            #d  = model.NewIntVar(0, 2*radius_circles*radius_circles, 'd_%d_%d'  % (i, j))
            model.Add(coordx[j + i*num_circles_dim] - coordx[(j-1) + (i-1)*num_circles_dim] == dx)
            model.Add(coordy[j + i*num_circles_dim] - coordy[(j-1) + (i-1)*num_circles_dim] == dy)
            constraints_distance(dx, dy, radius_circles, radius_circles)
        if j > 0:
            dx = model.NewIntVar(-size_area, size_area, 'dx_%d_%d' % (i, j))
            dy = model.NewIntVar(-size_area, size_area, 'dy_%d_%d' % (i, j))
            model.Add(coordx[j + i*num_circles_dim] - coordx[(j-1) + i*num_circles_dim] == dx)
            model.Add(coordy[j + i*num_circles_dim] - coordy[(j-1) + i*num_circles_dim] == dy)
            model.Add(coordx[j + i*num_circles_dim] - coordx[(j-1) + i*num_circles_dim] >= 0)
            constraints_distance(dx, dy, radius_circles, radius_circles)
        if i > 0:
            dx = model.NewIntVar(-size_area, size_area, 'dx_%d_%d' % (i, j))
            dy = model.NewIntVar(-size_area, size_area, 'dy_%d_%d' % (i, j))
            model.Add(coordx[j + i*num_circles_dim] - coordx[j + (i-1)*num_circles_dim] == dx)
            model.Add(coordy[j + i*num_circles_dim] - coordy[j + (i-1)*num_circles_dim] == dy)
            model.Add(coordy[j + i*num_circles_dim] - coordy[j + (i-1)*num_circles_dim] >= 0)
            constraints_distance(dx, dy, radius_circles, radius_circles)
# check num_circles_dim==2
#model.Add(coordx[0 + 1*num_circles_dim] == 142)
#model.Add(coordy[0 + 1*num_circles_dim] == 0)
#model.Add(coordx[1 + 0*num_circles_dim] == 0)
#model.Add(coordy[1 + 0*num_circles_dim] == 142)
#model.Add(coordx[1 + 1*num_circles_dim] == 142)
#model.Add(coordy[1 + 1*num_circles_dim] == 142)

print(border)
# minimize sum of border vars
#model.Minimize(sum(var for var in border))
model.Minimize(cp_model.LinearExpr.Sum(border))


##################################################################################
# INVOKE THE SOLVER

# Creates the solver and solve.
solver = cp_model.CpSolver()
solver.parameters.num_workers = 16
solver.parameters.linearization_level = 1
solver.parameters.log_search_progress = True
solver.parameters.log_to_stdout       = True
solver.parameters.log_to_response     = False
solver.parameters.cp_model_presolve   = True

status = solver.Solve(model)
#print(solver.status_name())


##################################################################################
# Statistics
print('\nStatistics')
print(f'Optimal border-sum: {solver.ObjectiveValue()}')
print(' - conflicts: %i' % solver.NumConflicts())
print(' - branches : %i' % solver.NumBranches())
print(' - wall time: %fs' % solver.WallTime())

# CHECK RESULT
if status != cp_model.OPTIMAL and status != cp_model.FEASIBLE:
    print('No solution found.')
    exit(1)    

##################################################################################
# SOLUTION
print("Solution: ")
for i, x in enumerate(coordx):
    print("(", solver.Value(x), ",", solver.Value(coordy[i]), ")", end="")

csv = SolverStatsCSV("circlePacking.csv")
log_list = csv.write_stats(solver, "circles_%d_%d" % (num_circles_dim, radius_circles), None)
print("\n", log_list)
