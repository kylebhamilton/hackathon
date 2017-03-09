import requests
import json

SESSION = requests.Session()
BASE_URL = None
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


def get(relative_url):
  kwargs = {
    "url": "%s/%s" % (BASE_URL, relative_url),
    "headers": {"X-Auth-Token":TOKEN, "Content-Type":"application/json; ext=nn"},
    "verify": False
  }
  resp = SESSION.get(**kwargs)
  return resp.json()["result"]

