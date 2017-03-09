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

"""
from rest_example import *
login("10.16.24.9")

eqh_list = LIB.read_all_params('/col/eqh?filter={"sl":{"$exists":true},"$ancestorsIn":["/mit/me/1/eqh/sh,1"]}')["result"]

eqh_list = get("col/eq")["result"]
eqtyp_list = filter(lambda x: x != "cnone", [eqh["sl"]["eqtyp"] for eqh in eqh_list if (eqh["type"] == "slot")])


"""

