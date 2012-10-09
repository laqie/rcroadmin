from django.conf.urls import patterns, url

urlpatterns = patterns('sambausers.views',
       url(r'^$', 'index', name='sambausers_index'),
       url(r'^add/$', 'sambauser_add', name='sambauser_add'),
       url(r'^edit/(\w+)/$', 'sambauser_add', name='sambauser_edit'),
       #AJAX views
       url(r'^change_password/$', 'change_user_password', name='sambausers_change_password'),
#       url(r'^modify_user/$', 'modify_user', name='mailusers_modify_user'),
)