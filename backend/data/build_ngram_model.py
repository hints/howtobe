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
import csv

CONDITIONALS = {}
GLOBAL_CONDITIONALS = {}
GLOBAL_MARGINALS = {}
MARGINALS = {}
SMOOTHED_CONDITIONALS = {}

DEPTHS = [ -20, -15, -10, -5, 0, 5 ]

import pickle
import sys

SMOOTHED_DATA_FILENAME = "howtobe/backend/data/smoothed.pickle"
SALARY_DATA_FILENAME = "howtobe/backend/data/H1B_FY2010-cleaned data1.csv"
ROLE_DESCRIPTION_FILENAME = "howtobe/backend/data/role_descriptions.txt"

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

def PrettyPrintJob( jobString ):

	'''
	Expects job string in the format
	job:0012
	'''

        roleId = int( jobString.split( ':' )[1] )
        idToRole = {}

	with open( ROLE_DESCRIPTION_FILENAME, 'rb' ) as csvfile:
	    rolesreader = csv.reader(csvfile, delimiter=',', quotechar='|')
	    for row in rolesreader:
		 if len( row[0] ) == 0 or ( len( row[0] ) > 0 and row[0][0] == '#' ):
		     continue
		 role = ''
		 if len(row) > 2:
		     for element in row[:-1]:
		         role = role + element
		 else:
		     role = row[0]

		 if int( row[-1] ) in idToRole:
		     idToRole[ int( row[-1] ) ].append( role )
		 else:
		     idToRole[ int( row[-1] ) ] = [ role ]

	if roleId not in idToRole.keys():
	    raise Exception( "Job ID not found" )
	
	shortestRoleName = ''
	for roleName in idToRole[ roleId ]:
	    if shortestRoleName == '' or ( len( roleName ) < len( shortestRoleName ) ):
	        shortestRoleName = roleName

	return shortestRoleName


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

            max_role = None
            max_count = 0
            for role, count in delta_metrics["roles"].items():
                if max_count < count:
                    max_role = role

            delta_metrics["max_role"] = max_role
            if d == 0:
                delta_metrics["max_role"] = role_id

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
    for i in range(20):
        f = open("howtobe/backend/data/v1.1/parsed_resumes.dat-%05d-of-%05d" % (i, SHARDS), "r")
        for j, career in enumerate(ResumeGenerator(f)):
            if j % 1000 == 0:
                print "processing career %d." % j
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

f = open("howtobe/backend/data/role_descriptions.txt", "r")
ROLE_DESCRIPTIONS = {}
for row in f:
    parts = row.split(",")
    if len(parts) < 2:
        continue
    a, b = parts[:2]
    if len(a) == 0:
        continue
    try:
        b = str(int(b))
    except:
        continue

    ROLE_DESCRIPTIONS[b] = a
    
f.close()

f = open("howtobe/backend/data/majors.txt", "r")
MAJORS = {}
for row in f:
    parts = row.split(",")
    if len(parts) < 3:
        continue
    major, id = parts[:2]
    if len(major) == 0:
        continue
    try:
        b = str(int(b))
    except:
        print "found bad row: %s " % str(parts)
        continue

    MAJORS[b] = a
    
f.close()


def PrettyName(role_id):
    def Capitalize(s):
        terms = []
        for term in s.split(" "):
            if term not in [ "of", "a", "and", "for", "the", "with", "or" ]:
                term = term.capitalize()
            terms.append(term)
        return " ".join(terms)

    parts = role_id.split(":")
    if parts[0] == "job":
        job_id = parts[1]
        job_name = ROLE_DESCRIPTIONS.get(job_id, None)
        if job_name == None:
            return None

        return Capitalize(job_name)

    elif parts[0] == "degree":
        degree_type = parts[1].upper()
        major = MAJORS.get(parts[1], None)
        if major == None:
            return None

        return "%s (%s)" % (Capitalize(job_name), degree_type)


def ComputeConditionals(ngram_pairs, roleIdToSalary):
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
    nodes = {}
    edges = {}

    for role, year_pairs in ngram_pairs.items():
        if role not in edges:
            edges[role] = {}

        if role not in nodes:
            nodes[role] = {}
            nodes[role]["time_jobs"] = {}
            nodes[role]["salary"] = 0

            roleId = int( role.split( ':' )[ 1 ] )
            if roleId in roleIdToSalary:
                nodes[role]["salary"] = int( round( roleIdToSalary[ roleId ] ) )
            
        for year_pair, role_data in year_pairs.items():
            y1, y2 = year_pair
            roles = {}

            for (r1, r2), count in role_data.items():
                if r1 == "None" or r2 == "None" or r1 is None or r2 is None:
                    continue

                if y1 not in nodes[role]["time_jobs"]:
                    nodes[role]["time_jobs"][y1] = []

                if r1 not in nodes[role]["time_jobs"][y1]:
                    nodes[role]["time_jobs"][y1].append({
                        "job_id": r1,
                        "weight": count["count"],
                        # TODO(gerrish): fix.
                        "pretty_name": PrettyName(r1),
                        "cluster_id": 0,
                        "number_job_changes": max(count["number_jobs"] - 1, 0) / count["count"],
                        "number_years_of_college": count["number_years_of_college"],
                        })
                
                if r1 not in roles:
                    roles[r1] = count
                else:
                    roles[r1] = AddDeltaMetrics(roles[r1], count)

            if year_pair not in edges:
                edges[role][year_pair] = {}

            for (r1, r2), count in role_data.items():
                if r1 == "None" or r2 == "None" or r1 == None or r2 == None:
                    continue
                
                if (r1, r2) not in edges[role][year_pair]:
                    c = count["count"]
                    edges[role][year_pair][(r1, r2)] = {
                        "weight": float(c / (roles[r1]["count"] + 0.01)),
                        "number_years_of_college": float(count["number_years_of_college"] / c),
                        "number_jobs": float(count["number_jobs"] / c),                        
                        }

    for role in nodes:
        for time in nodes[role]["time_jobs"]:
            weights = nodes[role]["time_jobs"][time]
            w = []
            total = 0.0
            for i, weight in enumerate(weights):
                total += weight["weight"]

            cum = 0.0
            weights.sort(key=lambda x: x["weight"], reverse=True)
            for i, weight in enumerate(weights):
                w.append(weight)
                cum += weight["weight"]
                weight["weight"] /= total
                if i >= 8:
                    break

            nodes[role]["time_jobs"][time] = w

    edges_out = {}
    for role in edges:
        edges_out[role] = []
        for (y1, y2) in edges[role]:
            for (r1, r2) in edges[role][(y1, y2)]:
                match = 0
                if y2 not in nodes[role]["time_jobs"]:
                    continue

                for node in nodes[role]["time_jobs"][y1]:
                    if node["job_id"] == r1:
                        match += 1
                        break

                for node in nodes[role]["time_jobs"][y2]:
                    if node["job_id"] == r2:
                        match += 1
                        break

                if match < 2:
                    continue

                edges_out[role].append((y1, r1, y2, r2, edges[role][(y1, y2)][(r1, r2)]["weight"]))

    return (nodes, edges_out)

def RoleIdToAverageSalary():

	roleToId = {}
	idToRole = {}

	with open( ROLE_DESCRIPTION_FILENAME, 'rb' ) as csvfile:
	    rolesreader = csv.reader(csvfile, delimiter=',', quotechar='|')
	    for row in rolesreader:
		 if len( row[0] ) == 0 or ( len( row[0] ) > 0 and row[0][0] == '#' ):
		     continue
		 role = ''
		 if len(row) > 2:
		     for element in row[:-1]:
		         role = role + element
		 else:
		     role = row[0]

		 if role in roleToId:
		     roleToId[ role ].append( int( row[-1] ) )
		 else:
		     roleToId[ role ] = [ int( row[-1] ) ]

		 if int( row[-1] ) in idToRole:
		     idToRole[ int( row[-1] ) ].append( role )
		 else:
		     idToRole[ int( row[-1] ) ] = [ role ]

	roles = roleToId.keys()

	represented = 0
	notRepresented = 0

	rolesWithSalary = set()
	roleIdToSalaryList = {}

	with open( SALARY_DATA_FILENAME, 'rb' ) as csvfile:
	    jobsreader = csv.reader(csvfile, delimiter=',', quotechar='"')
	    skipFirst = True
	    for row in jobsreader:
		if skipFirst:
		    skipFirst = False
		    continue

		role = row[13].lower() 

		if role in roles:
		    represented = represented + 1
		    rolesWithSalary.add( role )
		else:
		    notRepresented = notRepresented + 1
		    continue

		salary = None
		lowerSalary = float( row[14] )
		upperSalary = None
		if row[15] != '':
		    upperSalary = float( row[15] )
		if upperSalary:
		    salary = ( lowerSalary + upperSalary ) / 2.0
		else:
		    salary = lowerSalary
		
		for roleId in roleToId[ role ]:
		    if roleId in roleIdToSalaryList:
		        roleIdToSalaryList[ roleId ].append( salary )
		    else:
		        roleIdToSalaryList[ roleId ] = [ salary ]



	roleIdToAverageSalary = {}

	for roleId in roleIdToSalaryList:
	    roleIdToAverageSalary[ roleId ] = sum( roleIdToSalaryList[ roleId ] ) / float( len( roleIdToSalaryList[ roleId ] ) )

        return roleIdToAverageSalary

def LoadEdgeWeights():
    f = open(SMOOTHED_DATA_FILENAME, "r")
    tals_data = pickle.load(f)
    f.close()

if __name__ == '__main__':
    ngram_pairs = CollectNGramStats()

    roleIdToAverageSalary = RoleIdToAverageSalary()

    nodes, edges = ComputeConditionals(ngram_pairs, roleIdToAverageSalary)

    print nodes["job:2300"]
    #print edges["job:2300"]
    
    data = { "nodes": nodes, "edges": edges }
    f = open(SMOOTHED_DATA_FILENAME, "w")
    pickle.dump(data, f)
    f.close()

    #LoadEdgeWeights()
    

    # print PrettyPrintJob( 'job:1000030'	 )
