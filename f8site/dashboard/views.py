from datetime import datetime
from collections import OrderedDict
import json
import re

from django.http import HttpResponse, JsonResponse, Http404
from django.template import loader
from django.shortcuts import render

from rest import AdvaRestSession


def get_row(card_pms, left_uri, left_rx, left_tx, right_uri, right_rx, right_tx):
  row_dict = {
    "left": {},
    "right": {},
  }

  for (side, uri, rx, tx) in [("left", left_uri, left_rx, left_tx), ("right", right_uri, right_rx, right_tx)]:
    if uri and (uri in card_pms):
      row_dict[side] = {"label" : uri}
      if rx:
        row_dict[side]["rx"] = {
          "name"  : "%s: %s" % (uri, rx),
          "lo"    : card_pms[uri][rx]["thrl"],
          "cur"   : card_pms[uri][rx]["curr"],
          "hi"    : card_pms[uri][rx]["thrh"],
        }
      if tx:
        row_dict[side]["tx"] = {
          "name"  : "%s: %s" % (uri, tx),
          "lo"    : card_pms[uri][tx]["thrl"],
          "cur"   : card_pms[uri][tx]["curr"],
          "hi"    : card_pms[uri][tx]["thrh"],
        }

  return row_dict

"""
left_uri = ptp/cl,1/optm
right_uri = ptp/nw,1/opt

 OrderedDict([('ptp/cl,1/optm', OrderedDict([(u'opt', {'thrl': 0, 'curr': 7.4, 'thrh': 0}), (u'opr', {'thrl': 0, 'curr': 8.1, 'thrh': 0})])), ('ptp/cl,2/optm', OrderedDict([(u'opt', {'thrl': 0, 'curr': -60, 'thrh': 0}), (u'opr', {'thrl': 0, 'curr': -60, 'thrh': 0})])), ('ptp/cl,3/optm', OrderedDict([(u'opt', {'thrl': 0, 'curr': -60, 'thrh': 0}), (u'opr', {'thrl': 0, 'curr': -60, 'thrh': 0})])), ('ptp/cl,4/optm', OrderedDict([(u'opt', {'thrl': 0, 'curr': -60, 'thrh': 0}), (u'opr', {'thrl': 0, 'curr': -60, 'thrh': 0})])), ('ptp/nw,1/opt', OrderedDict([(u'opt', {'thrl': 0, 'curr': 0, 'thrh': 6}), (u'opr', {'thrl': -18, 'curr': -3.8, 'thrh': 0})])), ('ptp/nw,2/opt', OrderedDict([(u'opt', {'thrl': 0, 'curr': 0.1, 'thrh': 6}), (u'opr', {'thrl': -18, 'curr': -10.9, 'thrh': 0})]))])
"""

def index(request):
  if "ip" in request.GET:
    session = AdvaRestSession(request.GET["ip"])

    data = []
    pm_data = session.get_optical_pms()
    for (card_uri, card_pms) in pm_data.iteritems(): #session.get_cards(True):
      card = session.get(card_uri)

      rows = []
      if card["card"]["type"] == "qflex":
        rows.append(get_row(card_pms,
                            "ptp/cl,1/optm", "opr", "opt",
                            "ptp/nw,1/opt",  "opr", "opt"))
        rows.append(get_row(card_pms,
                            "ptp/cl,3/optm", "opr", "opt",
                            "ptp/nw,2/opt",  "opr", "opt"))
      elif card["card"]["type"] == "fd40d24l":
        rows.append(get_row(card_pms,
                            "ptp/nw,1/ctp/oms/oms", None,  "opr",
                            "ptp/nw,1/opt",         "opr", None))
      else:
        rows.append(get_row(card_pms,
                            "ptp/cl,1/opt", "opr", "opt",
                            "ptp/nw,1/opt", "opr", "opt"))

      data.append({
        "addr": card["dnm"],
        "name": card["name"],
        "rows": rows,
      })

    context = {
      "data": data,
    }
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


