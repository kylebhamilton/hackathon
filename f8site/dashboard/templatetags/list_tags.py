from django import template

register = template.Library()

@register.simple_tag
def get_value(dict_or_list, key):
    return dict_or_list[key]

@register.simple_tag
def get_entity_value(entity, key):
    if key in ["type", "id", "name", "status"]:
        return getattr(entity, key)
    else:
        return entity[key].value

@register.inclusion_tag('dashboard/table.html')
def show_table(headings, table_rows):
    context = {
        'headings': headings,
        'rows': table_rows,
    }
    return context

