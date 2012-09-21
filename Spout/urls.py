from django.conf.urls import patterns, include, url
import django
import Spout

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('Spout.views',
    # Examples:
    # url(r'^$', 'Spout.views.home', name='home'),
    # url(r'^Spout/', include('Spout.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
     url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
     url(r'^admin/', include(admin.site.urls)),
     url(r'^$', 'app_homepage'),
     url(r'^upload', 'upload_build'), 
     url(r'^apps/list', 'apps'), 
     url(r'^apps/plist/(?P<app_name>\w+)/(?P<app_version>.+)', 'get_plist'),
     url(r'^apps/ipa/(?P<app_name>\w+)/(?P<app_version>.+)', 'get_ipa'),
     url(r'^apps/dsym/(?P<app_name>\w+)/(?P<app_version>.+).dSYM', 'get_dsym'),
     url(r'^app/(?P<app_id>\w+)/approve', 'approve_app'),
     url(r'^app/(?P<app_id>\w+)/unapprove', 'unapprove_app'),
     url(r'^app/(?P<app_id>\w+)/tag/(?P<tag_name>\w+)', 'toggle_tag'),
     url(r'^app/(?P<app_id>\w+)/tag', 'app_tag'),
     url(r'^apps/tag/(?P<tag_name>\w+)', 'tagged_apps'),
     url(r'^app/tags/all', 'all_tags'),

     url(r'^crash/report/post', 'post_crash'),
)

urlpatterns += patterns('', 
        url(r'^accounts/login/$', 'django.contrib.auth.views.login'),
        url(r'^accounts/logout/$', 'django.contrib.auth.views.logout'),
        )

if Spout.settings.DEBUG:
    urlpatterns += patterns('',
                    (r'^media/(?P<path>.*)$', 'django.views.static.serve', 
                        {'document_root': Spout.settings.MEDIA_ROOT,
                            'show_indexes':True}),
                    (r'static/(?P<path>.*)$', 'django.views.static.serve',
                        {'document_root': Spout.settings.STATIC_ROOT,
                            'show_indexes':True}),
                    )
