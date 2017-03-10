from datetime import datetime
from collections import OrderedDict
import json
import re

from django.http import HttpResponse, JsonResponse, Http404
from django.template import loader
from django.shortcuts import render

from rest import AdvaRestSession


def index(request):
  if "ip" in request.GET:
    session = AdvaRestSession(request.GET["ip"])

    cards = []
    pm_data = session.get_optical_pms()
    for (uri, pm_data) in pm_data.iteritems(): #session.get_cards(True):
      card_dict = session.get(uri)
      cports = [v for (k, v) in pm_data.iteritems() if "ptp/cl," in k]
      nports = [v for (k, v) in pm_data.iteritems() if "ptp/nw," in k]
      cards.append((
        card_dict["dnm"],
        card_dict["name"],
        json.dumps(cports, indent=2),
        json.dumps(nports, indent=2),
      ))

    context = {
      "cards": cards,
    }
    print "context = %s" % context
    return render(request, 'dashboard/dashboard.html', context)
  else:
    return HttpResponse("Missing ip in URL")


def pm(request):
  if ("uri" in request.GET) and ("pm_name" in request.GET):
    return HttpResponse("You're displaying a PM: (%s, %s)" % (request.GET["uri"], request.GET["pm_name"]))
  else:
    raise Http404("Invalid PM URL")

def pm_json(request):
  session = AdvaRestSession(request.GET["ip"])

  if "uri" in request.GET:
    pm_name = request.GET.get("pm_name")
    data = session.get_optical_pm(request.GET["uri"], pm_name)
  else:
    data = session.get_optical_pms()
  return JsonResponse(data, safe=False)


def pm_hist_json(request):
  session = AdvaRestSession(request.GET["ip"])
  result = session.get("/mit/me/1/eqh/shelf,1/eqh/slot,2/eq/card/ptp/nw,1/opt/pm/hist")["result"]

  pm_types = ["oprl", "oprm", "oprh", "optl", "optm", "opth"]
  pm_data = OrderedDict([(t, OrderedDict()) for t in pm_types])
  for bin in [b for b in result if b["bintv"] == "m15"]:
    time_stamp = datetime.strptime(bin["stime"], "%Y-%m-%dT%H:%M:%SZ")
    for pm_type in pm_types:
      pm_data[pm_type][time_stamp] = bin["pmdata"][pm_type]

  # assemble json data array
  json_data = []
  for pm_type in pm_data:
    json_data.append({
      'key': pm_type,
      'values': [{'x':x, 'y':y} for (x, y) in pm_data[pm_type].items()],
    })

  return JsonResponse(json_data, safe=False)

def pm_hist(request):
  context = {
    'json_url': "%s.json?%s" % (request.path_info, request.META['QUERY_STRING']),
  }
  return render(request, 'dashboard/pm_hist.html', context)


