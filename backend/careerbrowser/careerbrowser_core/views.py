from django.shortcuts import render
from django.http import HttpResponse
from django.template import RequestContext, Context, loader
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.shortcuts import render_to_response
import json

# Create your views here.

def home(request):
	if settings.GLOVAR:
		settings.GLOCOUNT += 1
		return render_to_response('careerbrowser/index.html')
		#return HttpResponse(settings.GLOVAR + str(settings.GLOCOUNT))
	else:
		return HttpResponse("no global")

def home2(request):
        return render_to_response('careerbrowser/test2.html')

#exempting from safeguard against XSS attacks
#DONT DO THIS
# @csrf_exempt
# def api_handler(request):
# 	if request.method == 'GET':
# 		print("API CALL MADE")
# 		return HttpResponse("Use POST to request API data pl0x")
# 	elif request.method == 'POST':
# 		return HttpResponse("API CALL MADE!\n")#, context_instance=RequestContext(request))
# 	#http response as POST

# @csrf_exempt
# def api_handler(request, profession):
# 	print(profession)
# 	if request.method == 'GET':
# 		print("API CALL MADE")
# 		return HttpResponse("Use POST to request API data please")
# 	elif request.method == 'POST':
# 		nodes = settings.R_DATA["nodes"].get(profession, None)
# 		edges = settings.R_DATA["edges"].get(profession, None)
# 		res = { "edges": edges, "nodes": nodes}
# 		if(res.get("edges") is None or res.get("nodes is None")): #bug dontfix :|
# 			return(json.dumps({}))

# 		#return HttpResponse("API CALL MADE!\n")#, context_instance=RequestContext(request))
# 		return HttpResponse(json.dumps(res))

@csrf_exempt
def api_handler(request, profession):
	#print(profession)
	##nodes = settings.R_DATA["nodes"].get(profession, None)
	##edges = settings.R_DATA["edges"].get(profession, None)
	##res = { "edges": edges, "nodes": nodes}
	##if(res.get("edges") is None or res.get("nodes") is None):
	##	return(json.dumps({}))

	#return HttpResponse("API CALL MADE!\n")#, context_instance=RequestContext(request))
	#return HttpResponse(json.dumps(res))
	return HttpResponse(json.dumps({"edges" : settings.R_DATA["edges"].get(profession, None), "nodes" : settings.R_DATA["nodes"].get(profession, None)}))

def RoleIdFromQuery(q):
    q = q.lower()
    if ":" in q:
        return q

    if q in PROFESSIONS:
        return PROFESSIONS[q]

@csrf_exempt
def api_handler(request, profession):
    profession = RoleIdFromQuery(profession)
	if request.method == 'GET':
		print("API CALL MADE")
		return HttpResponse("Use POST to request API data please")
	elif request.method == 'POST':
		nodes = settings.R_DATA["nodes"].get(profession, None)
		edges = settings.R_DATA["edges"].get(profession, None)
		res = { "edges": edges, "nodes": nodes}
		if(res.get("edges") is None or res.get("nodes is None")): #bug dontfix :|
			return(json.dumps({}))

		#return HttpResponse("API CALL MADE!\n")#, context_instance=RequestContext(request))
		return HttpResponse(json.dumps(res))
