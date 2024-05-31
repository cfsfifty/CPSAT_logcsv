# class SolverStatsCSV

Write CP-SAT solver statistics to a CSV file given as csv_filename,
activated in CP-SAT as

<pre><code>
solver.parameters.log_search_progress = True
solver.parameters.log_to_response     = True
</code></pre>

Additionally, get the bound/objective history from the CP-SAT log response string.
Returned as a time-ordered list (time, bound, objective, gap[%]).

<pre><code>
responseString = str(solver.ResponseProto())
</code></pre>

Please see the example testCircles_FromLog.py.
