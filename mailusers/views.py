# coding=utf-8
from annoying.decorators import render_to, ajax_request

from django.utils import simplejson
from django.http import Http404
from django.shortcuts import get_object_or_404

from mailusers.models import MailUser
from mailusers.forms import MailUserForm



@render_to('mailusers/add.html')
def edit(request, username=None):
    user = get_object_or_404(MailUser, username=username) if username else None
    if user:
        title = u'Изменить пользователя "%s"' % user.dn
    else:
        title = u'Добавить нового пользователя почты'

    if request.method == 'POST':
        form = MailUserForm(request.POST, instance=user)
        if form.is_valid():
            user = form.save()
            title = u'Пользователь обновлен' if user else u'Пользователь добавлен'
            return dict(user=user, TEMPLATE='mailusers/edit_complete.html')
    else:
        form = MailUserForm(instance=user)


    return dict(form=form, title=title)

@render_to('mailusers/index.html')
def index(request):
    mailusers = MailUser.objects.order_by('username')
    title = u'Пользователи почты'
    return dict(mailusers=mailusers, title=title)


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
        active = data.get('active', 1)
        username = data.get('username', '')
        message = u'разблокирован' if active else u'заблокирован'
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
