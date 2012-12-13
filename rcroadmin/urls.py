from django.conf.urls import patterns, url, include
from django.views.generic import TemplateView

# Uncomment the next two lines to enable the admin:
#from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', TemplateView.as_view(template_name='index.html'), name='index'),
    url(r'^mailusers/', include('mailusers.urls')),
    url(r'^sambausers/', include('sambausers.urls')),

    url(r'^login/$', 'django.contrib.auth.views.login', {'template_name': 'login.html'}, name='login'),
    url(r'^logout/$', 'django.contrib.auth.views.logout', name='logout'),


)

from django.conf import settings
if settings.DEBUG:
    from django.contrib.staticfiles.urls import staticfiles_urlpatterns

    urlpatterns += staticfiles_urlpatterns()
    urlpatterns += patterns('django.views', (r'^%s(?P<path>.*)$' % settings.MEDIA_URL[1:],
                                             'static.serve',
                                             {'document_root': settings.MEDIA_ROOT}))
