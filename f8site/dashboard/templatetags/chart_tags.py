from django import template

from datetime import datetime
from collections import OrderedDict

register = template.Library()

@register.inclusion_tag('dashboard/linechart.html')
def line_chart2(chart_name, json_url, **kwargs):
    chart_data = OrderedDict()
    chart_data['Changes'] = json_url

    print "chart_name = %s" % chart_name
    print "json_url = %s" % json_url
    print "kwargs = %s" % kwargs

    return {
        'chart_name': chart_name,
        'chart_data': chart_data,
        'chart_height': kwargs.get("height", None),
        'chart_width': kwargs.get("width", None),

        'x_label': "Time",
        'x_is_date': True,
        'y_label': "Defects",
    }

@register.inclusion_tag('dashboard/lineplusbarchart.html')
def line_chart(chart_name, json_url, **kwargs):
    return {
        'json_url': json_url,
        'chart_name': chart_name,
        'chart_height': kwargs.get("height", 600),
        'chart_width': kwargs.get("width", 800),

        'x_label': "Time",
        'x_is_date': True,
        'y1_label': "Defects",
        'y2_label': "Code Changes",
    }
