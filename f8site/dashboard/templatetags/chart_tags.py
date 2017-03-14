from django import template

from datetime import datetime
from collections import OrderedDict

register = template.Library()

@register.inclusion_tag('dashboard/gauge.html')
def gauge(name, lo, cur, hi):
  if (lo == 0) and (hi == 0):
    lo = -30
    hi = 20

  hilo_delta = hi - lo
  _min = min(lo - (hilo_delta / 5), cur)
  _max = max(hi + (hilo_delta / 5), cur)

  if (cur < _min):
    _min = cur
  if (cur > _max):
    _max = cur

  return {
    "name": name,
    "unit": "dBm",
    "min" : _min,
    "lo"  : lo,
    "cur" : cur,
    "hi"  : hi,
    "max" : _max,
  }


