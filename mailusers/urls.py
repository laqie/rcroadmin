from django.conf.urls import patterns, url

urlpatterns = patterns('mailusers.views',
    url(r'^$', 'index', name='mailusers_index'),

    #AJAX views
    url(r'^get_password/$', 'get_user_password', name='mailusers_get_password'),
    url(r'^modify_user/$', 'modify_user', name='mailusers_modify_user'),
)
  