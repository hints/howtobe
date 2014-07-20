from django.shortcuts import render
from django.http import HttpResponse
from django.template import RequestContext
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings

# Create your views here.

def home(request):
	if settings.GLOVAR:
		settings.GLOCOUNT += 1
		return HttpResponse(settings.GLOVAR + str(settings.GLOCOUNT))#"global!")
	else:
		return HttpResponse("no global")

#	return HttpResponse("Hello!")

#exempting from safeguard against XSS attacks
#DONT DO THIS
@csrf_exempt
def api_handler(request):
	if request.method == 'GET':
		print("API CALL MADE")
		return HttpResponse("Use POST to request API data pl0x")
	elif request.method == 'POST':
		return HttpResponse("API CALL MADE!\n")#, context_instance=RequestContext(request))
	#http response as POST

# def api_handler(request):
# 	if request.method == 'GET':
# 		print("API CALL MADE")
# 		return HttpResponse("Use POST to request API data pl0x")
# 	elif request.method == 'POST':
# 		c = RequestContext(c, {'key':'value'})
# 		#return HttpResponse(c)
# 		return render_to_response("teaset",c)
