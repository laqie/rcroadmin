# coding=utf-8
from annoying.decorators import render_to, ajax_request
from sambausers.models import SambaGroup, SambaUser, create_or_change_user
from django.shortcuts import get_object_or_404
from django.http import Http404

from django.views.generic import ListView, FormView
from django.utils import simplejson

from sambausers.forms import SambaUserForm, SambaGroupForm


class SambaUsersView(ListView):
    template_name = 'sambausers/index.html'
    model = SambaUser
    context_object_name = 'users'

    def get_queryset(self):
        return SambaUser.objects.exclude(username__in=['root', 'nobody']).all()


class AddSambaGroupView(FormView):
    model = SambaGroup
    form_class = SambaGroupForm
    template_name = u'sambausers/group_add.html'


    def get_form_kwargs(self):
        kwargs = super(AddSambaGroupView, self).get_form_kwargs()
        kwargs[u'group_gid'] = self.kwargs.get(u'group_gid', 0)
        return kwargs


    def get_context_data(self, **kwargs):
        context = super(AddSambaGroupView, self).get_context_data(**kwargs)
        context['title'] = u'Добавить новую группу'
        return context


class SambaGroupsViews(ListView):
    template_name = 'sambausers/index_group.html'
    model = SambaGroup
    context_object_name = 'groups'

    def get_queryset(self):
        return SambaGroup.objects.exclude(gid_number__in=[513, 515]).all()


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
                    message = 'Пароль слишком короткий'
            else:
                message = 'Пароль не задан'
            return {'message': message}
    raise Http404
