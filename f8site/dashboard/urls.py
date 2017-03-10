from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),

    url(r'^pm.json$', views.pm_json, name='pm_json'),
    url(r'^pm$', views.pm, name='pm'),

    url(r'^pm_hist.json$', views.pm_hist_json, name='pm_hist_json'),
    url(r'^pm_hist$', views.pm_hist, name='pm_hist'),
]

