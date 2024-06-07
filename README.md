# class SolverStatsCSV

Write CP-SAT solver statistics to a CSV file given as csv_filename,
activated in CP-SAT as

<pre><code>
solver.parameters.log_search_progress = True
solver.parameters.log_to_response     = True
</code></pre>

CSV table schema, where objective1 == objective2 (and corresponding time and bound)
<pre><code>
[
'Date', 'ModelName', 'Objective', 'UserTime', '#Booleans', '#Branches', '#Conflicts', 'SolverParameters', 'SolverLog',
'time1', 'bound1', 'objective1', 'time2', 'bound2', 'objective2'
]
</code></pre>

Additionally, get the bound/objective history from the CP-SAT log response string after solving.
Then write_stats extracts and returns a time-ordered list log_list = [ (time, bound, objective, gapInPercent) ].
Please see the example testCircles_FromLog.py.

<pre><code>
responseString = str(solver.ResponseProto())
log_list = csv.write_stats(solver, "circles_%d_%d" % (num_circles_dim, radius_circles), responseString)
</code></pre>
