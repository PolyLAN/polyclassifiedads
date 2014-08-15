# -*- coding: utf-8 -*-

from django.conf.urls import patterns, url


urlpatterns = patterns('polyclassifiedads.views',
    url(r'^$', 'home'),
    url(r'^(?P<id>[0-9]*)$', 'show'),
    url(r'^browse$', 'browse'),
    url(r'^myads/$', 'my_ads'),
    url(r'^myads/new$', 'edit', {'id': None}, name='polyclassifiedads.views.new'),
    url(r'^myads/(?P<id>[0-9]*)/edit$', 'edit'),
    url(r'^myads/(?P<id>[0-9]*)/delete$', 'delete'),
    url(r'^myads/(?P<id>[0-9]*)/put_offline$', 'put_offline'),

    url(r'^search_in_tags$', 'search_in_tags'),

    url(r'^notifications/$', 'notifications'),
    url(r'^notifications/search$', 'search_in_categories'),

    url(r'^admin/$', 'unvalidated_list'),
    url(r'^admin/(?P<id>[0-9]*)/validate$', 'validate'),
    url(r'^admin/(?P<id>[0-9]*)/unvalidate$', 'unvalidate'),

)
