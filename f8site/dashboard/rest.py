import sys
import json
import requests
from collections import OrderedDict

from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

DEFAULT_CONTENT_TYPE = "application/json; ext=nn"

OPTICAL_PMS_BY_EQTYP = {
  "qflex": [
    "ptp/cl,1/opt",
    #"ptp/cl,1/optm/optl/1",
    #"ptp/cl,1/optm/optl/2",
    #"ptp/cl,1/optm/optl/3",
    #"ptp/cl,1/optm/optl/4",
    "ptp/cl,2/opt",
    #"ptp/cl,2/optm/optl/1",
    #"ptp/cl,2/optm/optl/2",
    #"ptp/cl,2/optm/optl/3",
    #"ptp/cl,2/optm/optl/4",
    "ptp/cl,3/opt",
    #"ptp/cl,3/optm/optl/1",
    #"ptp/cl,3/optm/optl/2",
    #"ptp/cl,3/optm/optl/3",
    #"ptp/cl,3/optm/optl/4",
    "ptp/cl,4/opt",
    #"ptp/cl,4/optm/optl/1",
    #"ptp/cl,4/optm/optl/2",
    #"ptp/cl,4/optm/optl/3",
    #"ptp/cl,4/optm/optl/4",
    "ptp/nw,1/opt",
    "ptp/nw,2/opt",
  ],

  "ams20p2": [
    "ptp/cl,1/opt",
    "ptp/nw,1/opt",
  ],

  "ams23l": [
    "ptp/cl,1/opt",
    "ptp/nw,1/opt",
  ],

  "fd40d24l": [
    "ptp/nw,1/opt",
  ],

  "ams23ltd": [
    "ptp/cl,1/opt",
    "ptp/nw,1/opt",
  ],
}

#QFLEX NETWORK
#slot_id=1
#port="nw"
#uri="/mit/me/1/eqh/shelf,%s/eqh/slot,%s/eq/card/ptp/%s,1/opt" % (shelf_id,slot_id,port)
#dict=get_pm(uri)
#print dict

#QFLEX CLIENT OPTM - currently broken
#slot_id=1
#port="cl"
#uri="/mit/me/1/eqh/shelf,%s/eqh/slot,%s/eq/card/ptp/%s,1/optm/optl/1" % (shelf_id,slot_id,port)
#dict=get_pm(uri)
#print dict


def print_as_json(data, indent=2):
  print json.dumps(data, indent=indent)

class AdvaRestSession(requests.Session):

  def __init__(self, ip_address, username="admin", password="CHGME.1a", **kwargs):
    super(AdvaRestSession, self).__init__(**kwargs)

    self.base_url = "https://%s:443" % ip_address
    self.username = username
    self.password = password
    self.token = None
    self.default_headers = None

    self.login(username, password)

    self.default_headers = {
      "X-Auth-Token":self.token,
      "Content-Type":DEFAULT_CONTENT_TYPE
    }

  def __del__(self):
    try:
      self.logout()
    except Exception, msg:
      print "Failed __del__(). Exception: %s" % msg


  def login(self, username="admin", password="CHGME.1a"):
    kwargs = {
      "url": "%s/auth?actn=lgin" % self.base_url,
      "headers": {"Content-Type":DEFAULT_CONTENT_TYPE},
      "data": json.dumps({"in":{"un":username, "pswd":password}}),
      "verify": False
    }
    resp = self.post(**kwargs)
    self.token = resp.headers["X-Auth-Token"]

  def logout(self):
    kwargs = {
      "url": "%s/auth?actn=lgout" % (self.base_url),
      "headers": self.default_headers,
      "verify": False
    }
    self.post(**kwargs)
    self.token = None


  def get(self, uri):
    kwargs = {
      "url": "%s/%s" % (self.base_url, uri.strip('/')),
      "headers": self.default_headers,
      "verify": False
    }
    resp = super(AdvaRestSession, self).get(**kwargs)
    return resp.json()

  def get_cards(self, filter_with_optical=False):
    card_list = []
    for eqh in self.get("col/eqh")["result"]:
      if (eqh["type"] == "slot") and (eqh["sl"]["eqtyp"] != "cnone"):
        eqtyp = eqh["sl"]["eqtyp"]
        if filter_with_optical and (eqtyp not in OPTICAL_PMS_BY_EQTYP):
          continue
        card_list.append((eqh["self"] + "/eq/card", eqtyp))
    #print card_list
    return card_list

  def get_optical_pm(self, uri, _pm_name=None):
    ##uri to interface
    ##example:
    ##  uri = /mit/me/1/eqh/shelf,%s/eqh/slot,%s/eq/card/ptp/nw,1/opt
    ##  pm_name = opr

    result_dict = OrderedDict()

    print "uri = %s" % uri

    pm_ent = self.get("%s/pm" % uri)["pment"]

    # Get current nint PM data
    crnt_dict = self.get("%s/pm/crnt" % uri)
    nint_dict = [item for item in crnt_dict["result"] if item['bintv'] == 'nint'][0]
    bintv = nint_dict["bintv"]
    prof_name = nint_dict["name"]

    for pm_name in nint_dict["pmdata"]:
      curr = nint_dict["pmdata"][pm_name]

      # Get TCA info from PM profile
      prof_dict = self.get("/mit/me/1/pmprof/%s,%s,%s" % (pm_ent, bintv, prof_name))
      tca_dict = [item for item in prof_dict["monspec"] if item['montyp']  == pm_name][0]
      thrl = tca_dict["thrl"]
      thrh = tca_dict["thrh"]

      # Build dictionary from all datas
      result_dict[pm_name] = OrderedDict()
      result_dict[pm_name]["min"] = thrl
      result_dict[pm_name]["cur"] = curr
      result_dict[pm_name]["max"] = thrh

    if _pm_name:
      return result_dict[_pm_name]
    else:
      return result_dict

  def get_optical_pms(self):
    is_print = True
    result_dict = OrderedDict()
    for (card_uri, eqtyp) in self.get_cards():
      if eqtyp in OPTICAL_PMS_BY_EQTYP:
        if is_print: print "(%s, %s):" % (card_uri, eqtyp)
        result_dict[card_uri] = OrderedDict()
        for rel_uri in OPTICAL_PMS_BY_EQTYP[eqtyp]:
          if is_print: print "  %s:" % (rel_uri)
          pm_uri = "%s/%s" % (card_uri, rel_uri)
          result_dict[card_uri][rel_uri] = self.get_optical_pm(pm_uri)
          if is_print:
            for (pm_name, values) in result_dict[card_uri][rel_uri].iteritems():
              print "    %s: %s" % (pm_name, values)

    return result_dict

def example(ip_address):
  session = AdvaRestSession(ip_address)

  print session.get_cards()


def main():
  print "Running example..."
  example(sys.argv[1])

if __name__ == "__main__":
    main()


