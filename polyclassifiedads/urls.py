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
    url(r'^notifications/search2$', 'search_in_types'),

    url(r'^admin/$', 'unvalidated_list'),
    url(r'^admin/(?P<id>[0-9]*)/validate$', 'validate'),
    url(r'^admin/(?P<id>[0-9]*)/unvalidate$', 'unvalidate'),


    url(r'^external/new$', 'external_edit', {'id': None}, name='polyclassifiedads.views.external_new'),

    url(r'^external/(?P<id>[0-9]*)$', 'external_show'),
    url(r'^external/(?P<id>[0-9]*)/edit$', 'external_edit'),
    url(r'^external/(?P<id>[0-9]*)/delete$', 'external_delete'),
    url(r'^external/(?P<id>[0-9]*)/put_offline$', 'external_put_offline'),


    url(r'^rss/(?P<user_id>[0-9]*)/(?P<key>[0-9a-f]*)$', 'rss'),

    url(r'^upload/$', 'jfu_upload', name='pca_jfu_upload'),
    url(r'^upload/delete/(?P<pk>\d+)$', 'jfu_delete', name='pca_jfu_delete'),

    url(r'^contact$', 'contact'),
    url(r'^cg$', 'cg'),
)
