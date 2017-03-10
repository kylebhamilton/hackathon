from django import template

from datetime import datetime
from collections import OrderedDict

register = template.Library()

@register.inclusion_tag('dashboard/gauge.html')
def gauge(name, lo, cur, hi):
  if (lo == 0) and (hi == 0):
    lo = cur - 10
    hi = cur + 10

  return {
    "name": name,
    "unit": "dBm",
    "min" : lo - ((hi - lo) / 5),
    "lo"  : lo,
    "cur" : cur,
    "hi"  : hi,
    "max" : hi + ((hi - lo) / 5),
  }


