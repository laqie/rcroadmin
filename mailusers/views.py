# coding=utf-8
from annoying.decorators import render_to, ajax_request
from mailusers.models import MailUser
from django.utils import simplejson
from django.http import Http404

@render_to('mailusers/index.html')
def index(request):
    mailusers = MailUser.objects.order_by('username')
    return dict(mailusers=mailusers)


@ajax_request
def get_user_password(request):
    if request.method == 'POST':
        data = simplejson.loads(request.POST.get('data', None))
        username = data.get('username', '')
        if username:
            user = MailUser.objects.get(username=username)
            return {'password': user.password}
    raise Http404


@ajax_request
def modify_user(request):
    if request.method == 'POST':
        data = simplejson.loads(request.POST.get('data', None))
        print data
        active = data.get('active', 1)
        username = data.get('username', '')
        message = u'включен' if active else u'отключен'
        html = u"""
            <div class="alert alert-block alert-warning hide fade in">
            <a class="close" data-dismiss="alert" href="#">&times;</a>
            <p>Пользователь "<strong>%s</strong>" был %s</p>
            </div>""" % (username, message)
        if username:
            user = MailUser.objects.get(username=username)
            user.active = active
            user.save()
            return {'alert': html}
    raise Http404
