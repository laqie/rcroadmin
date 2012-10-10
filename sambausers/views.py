# coding=utf-8
from annoying.decorators import render_to, ajax_request
from sambausers.models import SambaGroup, SambaUser, create_or_change_user, get_domain_info
from django.shortcuts import get_object_or_404
from django.http import Http404


from django.views.generic import ListView, FormView
from django.utils import simplejson

from sambausers.forms import SambaUserForm, SambaGroupForm



@render_to('sambausers/group_add.html')
def group_add(request, group_gid=None):
    group = get_object_or_404(SambaGroup, gid_number=group_gid) if group_gid else None
    title = u'Редактирование группы'
    if request.method == 'POST':
        form = SambaGroupForm(request.POST, instance=group)
        if form.is_valid():
            group = form.save(commit=False)
            if not group_gid:
                new_gid_number = SambaGroup.get_last_gid() + 1
                _, domain_sid, _, _ = get_domain_info()
                group.display_name = group.cn
                group.samba_group_type = 2
                group.gid_number = new_gid_number
                group.samba_sid = u'%s-%i' % (domain_sid, new_gid_number)
                group.save()
            else:
                group.display_name = group.cn
                group.save()
            title = u'Группа обновлена' if group_gid else u'Группа добавлена'
            return dict(group=group, title=title, TEMPLATE='sambausers/group_edit_complete.html')
    else:
        form = SambaGroupForm(instance=group)

    return dict(form=form, title=title)



@render_to('sambausers/group_index.html')
def group_index(request):
    groups = SambaGroup.objects.exclude(gid_number__in=[513, 515]).all()
    title = u'Группы домена'
    return dict(groups=groups, title=title)

@render_to('sambausers/index.html')
def index(request):
    sambausers = SambaUser.objects.exclude(username='root').exclude(username='nobody').all()
    title = u'Пользователи домена'
    return dict(sambausers=sambausers, title=title)


@render_to('sambausers/add.html')
def sambauser_add(request, username=None):
    if username:
        user = get_object_or_404(SambaUser, username=username)
        title = u'Редактирование пользователя: %s' % username
        initial = dict()
        initial['full_name'] = '%s %s' % (user.last_name, user.given_name)
        initial['username'] = user.username
        initial['clear_password'] = user.user_password
        initial['gecos'] = user.gecos
        initial['mail'] = user.mail[0] if len(user.mail) else ''
        initial['mobile'] = user.mobile
        initial['phone_number'] = user.phone
        initial['groups'] = user.user_groups_gids
    else:
        title = u'Добавить нового пользователя'
        initial = None

    if request.method == 'POST':
        form = SambaUserForm(username, request.POST, initial=initial)
        if form.is_valid():
            if username:
                data = dict()
                for field in form.changed_data:
                    if field in (u'username', u'clear_password'):
                        continue
                    data[field] = form.cleaned_data[field]
                groups = data.get('groups', None)
                if data:
                    user = create_or_change_user(username, **data)
                else:
                    user = SambaUser.objects.get(username=username)
                if groups is not None:
                    for group in SambaGroup.objects.exclude(gid_number=513).exclude(gid_number=515):
                        if str(group.gid_number) in groups:
                            group.add_member(username)
                        else:
                            group.remove_member(username)
                title = u'Пользователь обновлен'

            else:
                data = form.cleaned_data
                username = data.pop(u'username')
                groups = data.get('groups', 'None')
                user = create_or_change_user(username, **data)
                if groups is not None:
                    for group in SambaGroup.objects.exclude(gid_number=513).exclude(gid_number=515):
                        if str(group.gid_number) in groups:
                            group.add_member(username)
                        else:
                            group.remove_member(username)
                title = u'Пользователь добавлен'
            return dict(username=username, user=user, title=title, TEMPLATE='sambausers/edit_complete.html')
    else:
        form = SambaUserForm(username, initial=initial)

    return dict(form=form, title=title)


@ajax_request
def change_user_status(request):
    if request.method == 'POST':
        data = simplejson.loads(request.POST.get('data', None))
        username = data.get('username', '')
        if username:
            user = SambaUser.objects.get(username=username)
            if u'D' in user.samba_acct_flags:
                user.samba_acct_flags = u'[UX]'
                status = True
                message = u'Пользователь <strong>%s</strong> был разблокирован' % username
            else:
                status = False
                user.samba_acct_flags = u'[UXD]'
                message = u'Пользователь <strong>%s</strong> был заблокирован' % username
            user.save()
            return {'message': message, 'status': status}
    raise Http404


@ajax_request
def delete_user(request):
    if request.method == 'POST':
        data = simplejson.loads(request.POST.get('data', None))
        username = data.get('username', '')
        if username:
            user = SambaUser.objects.get(username=username)
            message = u'Пользователь <strong>%s</strong> был удален' % username
            user.delete()
            return {'message': message}
    raise Http404


@ajax_request
def change_user_password(request):
    if request.method == 'POST':
        data = simplejson.loads(request.POST.get('data', None))
        username = data.get('username', '')
        if username:
            password = data.get('newpassword', '')
            if password:
                if len(password) >= 5:
                    user = SambaUser.objects.get(username=username)
                    user.change_password(password)
                    user.save()
                    message = u"""Пароль пользователя <strong>%s</strong> изменен на <strong>%s</strong>""" % (username, password)
                else:
                    message = u'Пароль слишком короткий'
            else:
                message = u'Пароль не задан'
            return {'message': message}
    raise Http404
