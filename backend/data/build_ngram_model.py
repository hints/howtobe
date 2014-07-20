#!/usr/bin/python

#!/usr/bin/python
#
# This script provides a service for bls jobs.
# The main functions exported are:
# next_steps
# previous_steps
import copy
import datetime
import pickle

CONDITIONALS = {}
GLOBAL_CONDITIONALS = {}
GLOBAL_MARGINALS = {}
MARGINALS = {}
SMOOTHED_CONDITIONALS = {}

DEPTHS = [ -20, -15, -10, -5, 0 ]

import pickle
import sys

TIMES = [ -20, -15, -10, -5, 0 ]

SMOOTHED_DATA_FILENAME = "howtobe/backend/data/smoothed.pickle"

def BuildNGrams():
    pass


class Career:
    def __init__(self, id):
        self.id = id
        self.jobs = []
        self.degrees = []
        self.career_start = None

        
def ResumeGenerator(f):
    c = None
    mode = None
    career_start = None
    for i, row in enumerate(f):
        row = row.strip()
        if len(row) == 0:
            continue
        if row == "### ID":
            if c != None:
                c.career_start = career_start
                yield c

            mode = row
        elif row == "### JOBS":
            mode = row
        elif row == "### EDUCATION":
            mode = row
        elif mode == "### EDUCATION":
            parts = row.split(",")
            try:
                start, end, _, degree, major, school = parts
            except:
                print "failed to parse parts." + str(parts)
                sys.exit(1)
            s = None
            e = None
            if start != "None":
                s = datetime.datetime.strptime(start, "%Y-%m-%d")
            if end != "None":
                e = datetime.datetime.strptime(end, "%Y-%m-%d")
            
            if e == None and s != None:
                e = s + datetime.timedelta(days=365)

            if s == None and e != None:
                s = e - datetime.timedelta(days=365)

            # TODO(gerrish): fix this.
            if e == None and s == None:
                continue

            if (e - s).days < 365:
                s = e - datetime.timedelta(days=365)

            if career_start is None:
                career_start = s
            if career_start is None:
                career_start = e - datetime.timedelta(days=365)

            c.degrees.append((s, e, degree, major, school))
                
        elif mode == "### JOBS":            
            parts = row.split(",")
            try:
                start, end, _, id, desc, _, _ = parts[:7]
            except:
                print "failed to parse parts." + str(parts)                
                sys.exit(1)
            s = None
            e = None
            if start != "None":
                s = datetime.datetime.strptime(start, "%Y-%m-%d")
            if end != "None":
                e = datetime.datetime.strptime(end, "%Y-%m-%d")

            s = None
            e = None
            if start != "None":
                s = datetime.datetime.strptime(start, "%Y-%m-%d")
            if end != "None":
                e = datetime.datetime.strptime(end, "%Y-%m-%d")
            
            if e == None and s != None:
                e = s + datetime.timedelta(days=365)

            if s == None and e != None:
                s = e - datetime.timedelta(days=365)

            # TODO(gerrish): fix this.
            if e == None and s == None:
                continue

            if (e - s).days < 365:
                s = e - datetime.timedelta(days=365)

            if career_start is None:
                career_start = s
            if career_start is None:
                career_start = e - datetime.timedelta(days=365)                
                
            c.jobs.append((s, e, id, desc))

        elif mode == "### ID":
            c = Career(row)
        else:
            print row
            sys.exit(1)


def Smooth(raw, smoothed):
    for key, value in raw:
        smoothed[key] = value

def StatsFromCareer():
    pass

def NewDeltaMetrics():
    return {
        "years": 0,
        "number_jobs": 0,
        "number_years_of_college": 0,
        "colleges": {},
        "degrees": {},
        "roles": {},
        "count": 1,
        "max_role": None,
        }

def AddDeltaMetrics(a, b):
    result = {}
    for key, value in a.items():
        if type(value) == type(0):
            result[key] = value + b[key]

    return result

def RoleFromDegree(degree, major):
    assert degree != "None"
    #assert major != "None"
    return "degree:%s:%s" % (degree, major)

def RoleFromJob(id):
    assert id != "None"
    return "job:%s" % str(id)

# Note that this function gives more weight to people who change
# jobs a lot.
def AddStats(ngram_marginals, ngram_pairs, career):
    if career is None:
        print "Skipping None career."
        return

    for job in career.jobs:
        (start, end, id, desc) = job
        if id == "None":
            continue
        role_id = RoleFromJob(id)


        last_delta_metrics = None

        for i, d in enumerate(DEPTHS):
            delta_metrics = NewDeltaMetrics()
            if i == len(DEPTHS) - 1:
                continue
            next_d = DEPTHS[i + 1]
            years_delta_start = start + datetime.timedelta(days=365 * d)
            years_delta_end = start + datetime.timedelta(days=365 * next_d)
            delta_metrics["years"] += 1

            for s2, e2, id2, _ in career.jobs:
                if id2 == "None":
                    continue
                r2_id = RoleFromJob(id2)
                c = s2
                while c < years_delta_start:
                    c += datetime.timedelta(days=365)

                while c < years_delta_end:
                    if r2_id not in delta_metrics["roles"]:
                        delta_metrics["roles"][r2_id] = 0
                    delta_metrics["roles"][r2_id] += 1
                    
                    c += datetime.timedelta(days=365)

                    
            max_role = None
            max_count = 0
            for role, count in delta_metrics["roles"].items():
                if max_count < count:
                    max_role = role

            delta_metrics["max_role"] = max_role

            
            for (s2, e2, degree, major, school) in career.degrees:
                if degree == "None":
                    continue
                degree_id = RoleFromDegree(degree, major)
                while c < years_delta_start:
                    c += datetime.timedelta(days=365)

                while c < years_delta_end:
                    if degree_id not in delta_metrics["roles"]:
                        delta_metrics["roles"][degree_id] = 0

                    delta_metrics["roles"][degree_id] += 1
                    delta_metrics["degrees"][degree_id] += 1
                    delta_metrics["years_of_college"] += 1
                    
                    c += datetime.timedelta(days=365)

            delta_metrics["number_jobs"] = len(delta_metrics["roles"])

            if last_delta_metrics == None:
                last_delta_metrics = delta_metrics
                continue
                
            if role_id not in ngram_pairs:
                ngram_pairs[role_id] = {}

            delta_pair = (d, next_d)
            if delta_pair not in ngram_pairs[role_id]:
                ngram_pairs[role_id][delta_pair] = {}
                
            if delta_pair not in ngram_pairs[role_id]:
                ngram_pairs[role_id][delta_pair] = {}

            pair = (last_delta_metrics["max_role"], delta_metrics["max_role"])
            if pair not in ngram_pairs[role_id][delta_pair]:
                ngram_pairs[role_id][delta_pair][pair] = last_delta_metrics
            else:
                ngram_pairs[role_id][delta_pair][pair] = AddDeltaMetrics(
                    last_delta_metrics,
                    ngram_pairs[role_id][delta_pair][pair])
                
            last_delta_metrics = delta_metrics


def CollectNGramStats():
    # In the form:
    # TODO: add degree counts
    # key - job_id, e.g., job:1402
    # value:
    """
    {
      -15: { max_job_id1: count1, # job id is the key
             max_job_id2: count2,
             ...
             "total": sum of all of these
           }
      -10
      -5
    }

    { key: role_id (string) : {
        (-15, -10): {
                    (max_job_id_time_-15_1, max_job_id_-10_1): count1,
                    (max_job_id_time_-15_2, max_job_id_-10_2): count2,
                  }
    }
    """
    ngram_marginals = {}
    ngram_pairs = {}

    SHARDS = 100
    for i in range(1):
        f = open("data/v1.1/parsed_resumes.dat-%05d-of-%05d" % (i, SHARDS), "r")
        for j, career in enumerate(ResumeGenerator(f)):
            if j % 100 == 0:
                print "processing career %d." % j
            if j > 100000:
                break
            AddStats(ngram_marginals, ngram_pairs, career)

        f.close()

    return ngram_pairs

    """
    for i, (key, value) in enumerate(ngram_pairs.items()):
        if i > 10:
            break
        for v, vv in value.items():
            print vv
    """

def ComputeConditionals(ngram_pairs):
    """
    key: role_id
    value: {
      key: pairs of integers giving delta compared to now, e.g. (-15, -10).
      value: {
        key: pairs of job_ids giving a job at time -15, -10, e.g. (job:1024, job:6078)
        value: {
             "weight": float(c / (roles[r1]["count"] + 0.01)),
             "number_years_of_college": float(count["number_years_of_college"] / c),
             "number_jobs": float(count["number_jobs"] / c),
        }
      }
    }
    """
    conditionals = {}

    for role, year_pairs in ngram_pairs.items():
        if role not in conditionals:
            conditionals[role] = {}

        for year_pair, role_data in year_pairs.items():
            roles = {}

            for (r1, r2), count in role_data.items():
                if r1 == "None" or r2 == "None":
                    continue

                if r1 not in roles:
                    roles[r1] = count
                else:
                    roles[r1] = AddDeltaMetrics(roles[r1], count)

            if year_pair not in conditionals:
                conditionals[role][year_pair] = {}

            for (r1, r2), count in role_data.items():
                if r1 == "None" or r2 == "None" or r1 == None or r2 == None:
                    continue
                
                if (r1, r2) not in conditionals[role][year_pair]:
                    c = count["count"]
                    conditionals[role][year_pair][(r1, r2)] = {
                        "weight": float(c / (roles[r1]["count"] + 0.01)),
                        "number_years_of_college": float(count["number_years_of_college"] / c),
                        "number_jobs": float(count["number_jobs"] / c),                        
                        }

                    #print (r1, r2), conditionals[role][year_pair][(r1, r2)]
            
    return conditionals

def LoadEdgeWeights():
    f = open(SMOOTHED_DATA_FILENAME, "r")
    tals_data = pickle.load(f)
    f.close()

    print tals_data.keys()

if __name__ == '__main__':
    ngram_pairs = CollectNGramStats()

    conditionals = ComputeConditionals(ngram_pairs)

    f = open(SMOOTHED_DATA_FILENAME, "w")
    pickle.dump(conditionals, f)
    f.close()

    LoadEdgeWeights()
