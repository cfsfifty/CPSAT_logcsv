import csv
import sys
import os
import locale
import datetime
import re
import math
from ortools.sat.python import cp_model

class SolverStatsCSV:
    ''' Write solver stats to a CSV file csv_filename. Additionally, get bound/objective history from log response string.
        Returned as time-ordered list. '''
    def __init__ (self, csv_filename : str):
        self.csv_filename = csv_filename
        self.csv_header   = ['Date', 'ModelName', 'Objective', 'UserTime', '#Booleans', '#Branches', '#Conflicts', 'SolverParameters', 'SolverLog', 'time1', 'bound1', 'objective1', 'time2', 'bound2', 'objective2' ]
        self.smonotonous  = False

    def set_strict_monotonous (self, smonotonous : bool):
        self.smonotonous = smonotonous
    def get_strict_monotonous (self) -> bool:
        return self.smonotonous

    def write_csvheader(self):
        if not os.path.exists(self.csv_filename): 
            # new file and write header
            with open(self.csv_filename, 'w', newline='') as csv_file:
                csv_out = csv.DictWriter(csv_file, fieldnames = self.csv_header, delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                csv_out.writeheader()

    @staticmethod
    def sol_gap (bound, objective, domain_bound):
        return (float(objective)-float(bound))/float(objective)


    def write_stats (self, cpsat_solver : cp_model.CpSolver, modelname : str, log_string : str) -> list:
        # all (newline, line-feed) with german formatting
        #locale.setlocale(locale.LC_ALL,     'de_DE.utf8')
        # numeric always with american formatting
        locale.setlocale(locale.LC_NUMERIC, 'en_US.utf8')            
        self.write_csvheader()
        
        stats_file = list() # (time, lower_bound, upper_bound, gap)
        
        # get current time
        now = datetime.datetime.now() 
        with open(self.csv_filename, 'a', newline='') as csv_file: # write data row to existing file
                # write data
                csv_out = csv.DictWriter(csv_file, fieldnames=self.csv_header, delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                row = {}
                row[self.csv_header[0]] = now.strftime('%Y-%m-%d_%H-%M')                      
                row[self.csv_header[1]] = modelname
                row[self.csv_header[2]] = int(cpsat_solver.ObjectiveValue())
                row[self.csv_header[3]] = int(math.floor(cpsat_solver.UserTime()*1000.0))
                row[self.csv_header[4]] = cpsat_solver.NumBooleans()
                row[self.csv_header[5]] = cpsat_solver.NumBranches()
                row[self.csv_header[6]] = cpsat_solver.NumConflicts()
                row[self.csv_header[7]] = str(cpsat_solver.parameters)

                if not log_string or log_string == "":
                    csv_out.writerow(row)
                    return stats_file

                # get bounds and objective from log_string
                time       = [ 0 ]
                bound      = [ 0 ]
                objective  = [ 0 ]
                gap        = 1.0 
                domain_bound = -1
                #locale.setlocale(locale.LC_NUMERIC, 'en_US.utf8') 
                for line in log_string.split('\\n'):
                        state = 0
                        #out   = ""
                        for word in line.split(' '):
                            # prefix
                            if re.match("#(\d+)", word) or re.match("#Bound", word):
                                state = 1
                            if re.match("#Done", word):
                                state = 2
                            # later word
                            if state > 0:
                                #print(word, " state line")
                                z = re.match("([\d\.]+)s", word)
                                if z:
                                    #print(z.groups()[0])
                                    value = int(math.floor(float(z.groups()[0])*1000.0)) # s to ms
                                    if value <= time[-1]: 
                                        if self.smonotonous:
                                            # make time[] strictly monotonous
                                            value = time[-1]+1 
                                        else:
                                            # make time[] monotonous (ordered in time)
                                            value = time[-1] 
                                    time[-1] = value
                                else:
                                    z = re.match("next:\[(\d+),(\d+)\]", word)
                                    if z:
                                        #print(z.groups)
                                        bound[-1]     = int(z.groups()[0])
                                        objective[-1] = int(z.groups()[1])+1
                                        if domain_bound == -1:
                                            # get domain bound after presolving
                                            domain_bound = objective[-1]
                                    else: # line '#(\d+) next:[] .*'
                                        z = re.match("next:\[\]", word)
                                        if z:
                                            state = 2
                        if state > 0:
                            if state == 1:
                                stats_file.append((time[-1], bound[-1], objective[-1], SolverStatsCSV.sol_gap(bound[-1], objective[-1], domain_bound)*100))
                                # add entries for next line
                                time .append(time[-1])  # last time
                                bound.append(bound[-1]) # last bound
                                objective.append(objective[-1]) # last upper bound
                            if state == 2:
                                stats_file.append((time[-1], bound[-1], objective[-1], SolverStatsCSV.sol_gap(bound[-1], objective[-1], domain_bound)*100))
                                break

                # "\r\n"
                log_string = log_string[log_string.find("obj") : -1].replace("\n", "\r\n")
                #print(log_string)
                row[self.csv_header[8]] = log_string

                assert(len(objective) == len(bound))
                assert(len(objective) == len(time))
                if len(objective) > 1:
                    # find lower bounds at min objective (especially first lower bound)
                    index_bounds = [ i for i in range(-1, -len(objective), -1) if objective[i] == objective[-1] ]
                    row[self.csv_header[9]]  = time [index_bounds[-1]]
                    row[self.csv_header[10]] = bound[index_bounds[-1]]     # first lower bound
                    row[self.csv_header[11]] = objective[index_bounds[-1]]
                else:
                    row[self.csv_header[9]]  = time [-1]
                    row[self.csv_header[10]] = bound[-1]
                    row[self.csv_header[11]] = objective[-1]
                row[self.csv_header[12]] = time [-1]
                row[self.csv_header[13]] = bound[-1]
                row[self.csv_header[14]] = objective[-1]
                csv_out.writerow(row)              
        return stats_file
