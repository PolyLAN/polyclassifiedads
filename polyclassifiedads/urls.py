# -*- coding: utf-8 -*-

from django.conf.urls import patterns, url


urlpatterns = patterns('polyclassifiedads.views',
    url(r'^$', 'home'),
    url(r'^myads/new$', 'edit', {'id': None}, name='polyclassifiedads.views.new'),
    url(r'^myads/(?P<id>[0-9]*)$', 'show'),

)
