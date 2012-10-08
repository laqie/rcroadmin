from django.conf.urls import patterns, url, include
from django.views.generic import TemplateView

# Uncomment the next two lines to enable the admin:
#from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    url(r'^$', TemplateView.as_view(template_name='index.html'), name='index'),
    url(r'^mailusers/', include('mailusers.urls')),
    # url(r'^rcroadmin/', include('rcroadmin.foo.urls')),
#    url(r'^mailusers/$', 'mailusers.views.index', name='mailusers_index'),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    #url(r'^admin/', include(admin.site.urls)),
)

from django.conf import settings
if settings.DEBUG:
    from django.contrib.staticfiles.urls import staticfiles_urlpatterns

    urlpatterns += staticfiles_urlpatterns()
    urlpatterns += patterns('django.views', (r'^%s(?P<path>.*)$' % settings.MEDIA_URL[1:],
                                             'static.serve',
                                             {'document_root': settings.MEDIA_ROOT}))
