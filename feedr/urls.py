from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^login/$', views.auth, name='auth'),
    url(r'^logout/$', views.deauth, name='deauth'),
    url(r'^list/$', views.list, name='list'),
    url(r'^$', views.list, name='list'),
    url(r'^list/(?P<limit>[0-9]+)/$', views.list, name='list'),
    url(r'^list/(?P<cat>[a-z]+)/(?P<limit>[0-9]+)/$', views.list, name='list'),
    url(r'^list/(?P<cat>[a-z]+)/$', views.list, name='list'),
    url(r'^fav/(?P<feedid>[0-9]+)/$', views.fav, name='fav'),
    url(r'^read/(?P<feedid>[0-9]+)/$', views.read, name='read'),
    url(r'^readall/$', views.readall, name='readall'),
    url(r'^refresh/$', views.refresh, name='refresh'),
    url(r'^favorites/$', views.favorites, name='favorites'),
    url(r'^favorites/(?P<cat>[a-z]+)/$', views.favorites, name='favorites'),
    url(r'^favorites/(?P<cat>[a-z]+)/(?P<limit>[0-9]+)/$', views.favorites, name='favorites'),
    url(r'^logs/$', views.logs, name='logs'),
]

