# class SolverStatsCSV

Write CP-SAT solver statistics to a CSV file given as csv_filename,
activated in CP-SAT as

solver.parameters.log_search_progress = True
solver.parameters.log_to_response     = True

Additionally, get the bound/objective history from the log response string.

Returned as a time-ordered list (time, bound, objective, gap[%]).

Please see the example testCircles_FromLog.py.
