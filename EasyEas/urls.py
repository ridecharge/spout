from django.conf.urls import patterns, include, url
import django
import EasyEas

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('EasyEas.views',
    # Examples:
    # url(r'^$', 'EasyEas.views.home', name='home'),
    # url(r'^EasyEas/', include('EasyEas.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
     url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
     url(r'^admin/', include(admin.site.urls)),
     url(r'^apps/list', 'apps'), 
     url(r'^apps/upload', 'upload_build'), 
     url(r'^apps/plist/(?P<app_name>\w+)/(?P<app_version>.+)', 'get_plist'),
     url(r'^apps/ipa/(?P<app_name>\w+)/(?P<app_version>.+)', 'get_ipa'),
)

if EasyEas.settings.DEBUG:
    urlpatterns += patterns('',
                    (r'^static/media/(?P<path>.*)$', 'django.views.static.serve', 
                        {'document_root':"/Users/akfreas/Development/easyeas_data/media",
                            'show_indexes':True}),
                    )
