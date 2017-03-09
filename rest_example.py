import requests
import json

from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

SESSION = requests.Session()
BASE_URL = None
HEADERS = None
TOKEN = None

def login(ip, un="admin", pswd="CHGME.1a"):
  global BASE_URL
  BASE_URL = "https://%s:443" % ip

  kwargs = {
    "url": "%s/auth?actn=lgin" % BASE_URL,
    "headers": {"Content-Type":"application/json; ext=nn"},
    "data": json.dumps({"in":{"un":un, "pswd":pswd}}),
    "verify": False
  }
  resp = SESSION.post(**kwargs)

  global TOKEN
  TOKEN = resp.headers["X-Auth-Token"]
  global HEADERS
  HEADERS = {
    "X-Auth-Token":TOKEN,
    "Content-Type":"application/json; ext=nn"
  }

def logout():
  kwargs = {
    "url": "%s/auth?actn=lgout" % (BASE_URL),
    "headers": HEADERS,
    "verify": False
  }
  resp = SESSION.post(**kwargs)

def get(relative_url):
  kwargs = {
    "url": "%s/%s" % (BASE_URL, relative_url.strip('/')),
    "headers": HEADERS,
    "verify": False
  }
  resp = SESSION.get(**kwargs)
  return resp.json()

def print_as_json(data, indent=2):
  print json.dumps(data, indent=indent)

def get_pm(uri):
  ##uri to interface
  ##example /mit/me/1/eqh/shelf,%s/eqh/slot,%s/eq/card/ptp/nw,1/opt

  #GET INTERFACE NAME
  dict= get(uri)
  interface_name=dict["fnm"]

  #GET MONITORING LAYER NAME
  pm=dict["pm"]
  pm_layer=pm["pment"]

  #GET ALL PM VALUES
  pm_uri="%s/pm/crnt" % uri
  dict= get(pm_uri)

  #FIND CURRENT PMs (nint)
  list=dict["result"]
  list_with_all_nint_pms= [element for element in list if element['bintv'] == 'nint']
  dict_with_all_nint_pms=list_with_all_nint_pms[0]

  #GET PM DATA
  bintv=dict_with_all_nint_pms["bintv"]
  pm_profile_name=dict_with_all_nint_pms["name"]
  dict_pm=dict_with_all_nint_pms["pmdata"]

  opr=dict_pm["opr"]
  opt=dict_pm["opt"]

  #GET OPT PM PROFILE
  uri="/mit/me/1/pmprof/%s,%s,%s" % (pm_layer, bintv, pm_profile_name)
  dict=get(uri)
  list=dict["monspec"]

  #GET OPR TCA
  list_opr= [element for element in list if element['montyp'] == 'opr']
  dict_opr=list_opr[0]
  #print dict_opr
  montype=dict_opr["montyp"]
  opr_l=dict_opr["thrl"]
  opr_h=dict_opr["thrh"]

  #GET OPT TCA
  list_opt= [element for element in list if element['montyp'] == 'opt']
  dict_opt=list_opt[0]
  montype=dict_opt["montyp"]
  opt_l=dict_opt["thrl"]
  opt_h=dict_opt["thrh"]

  #BUILD DICTIONARY FROM ALL DATAS
  pm_dict = {}
  pm_dict['opr_l'] = opr_l
  pm_dict['opr_h'] = opr_h
  pm_dict['opt_l'] = opt_l
  pm_dict['opt_h'] = opt_h
  pm_dict['opr'] = opr
  pm_dict['opt'] = opt
  pm_dict['if_name'] = interface_name

  #print pm_dict
  return pm_dict

#SYSTEM
ip="10.16.24.50"
shelf_id=1
login(ip)

#QFLEX NETWORK
slot_id=1
port="nw"
uri="/mit/me/1/eqh/shelf,%s/eqh/slot,%s/eq/card/ptp/%s,1/opt" % (shelf_id,slot_id,port)
dict=get_pm(uri)
print dict

#QFLEX CLIENT OPTM - currently broken
slot_id=1
port="cl"
uri="/mit/me/1/eqh/shelf,%s/eqh/slot,%s/eq/card/ptp/%s,1/optm/optl/1" % (shelf_id,slot_id,port)
dict=get_pm(uri)
print dict

#AMP NETWORK
slot_id=2
port="nw"
uri="/mit/me/1/eqh/shelf,%s/eqh/slot,%s/eq/card/ptp/%s,1/opt" % (shelf_id,slot_id,port)
dict=get_pm(uri)
print dict

#AMP CLIENT
slot_id=2
port="cl"
uri="/mit/me/1/eqh/shelf,%s/eqh/slot,%s/eq/card/ptp/%s,1/opt" % (shelf_id,slot_id,port)
dict=get_pm(uri)
print dict

"""
from rest_example import *
login("10.16.24.9")

eqh_list = LIB.read_all_params('/col/eqh?filter={"sl":{"$exists":true},"$ancestorsIn":["/mit/me/1/eqh/sh,1"]}')["result"]

eqh_list = get("col/eq")["result"]
eqtyp_list = filter(lambda x: x != "cnone", [eqh["sl"]["eqtyp"] for eqh in eqh_list if (eqh["type"] == "slot")])


card_list = []
for eqh in get("col/eqh")["result"]:
  if (eqh["type"] == "slot") and (eqh["sl"]["eqtyp"] != "cnone"):
    card_list.append(eqh["sl"]["eqtyp"])
    print eqh["sl"]
print card_list

"""



