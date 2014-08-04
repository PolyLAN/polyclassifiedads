# -*- coding: utf-8 -*-

from django.conf.urls import patterns, url


urlpatterns = patterns('polyclassifiedads.views',
    url(r'^$', 'home'),

)
