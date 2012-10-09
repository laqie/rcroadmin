from django.conf.urls import patterns, url

urlpatterns = patterns('sambausers.views',
       url(r'^$', 'index', name='sambausers_index'),
       url(r'^add/$', 'sambauser_add', name='sambauser_add'),
       url(r'^edit/(\w+)/$', 'sambauser_add', name='sambauser_edit'),

       #AJAX views
       url(r'^change_password/$', 'change_user_password', name='sambausers_change_password'),
       url(r'^change_status/$', 'change_user_status', name='sambausers_change_status'),
       url(r'^delete/$', 'delete_user', name='sambausers_delete_user'),
)