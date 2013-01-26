# -*- coding: utf-8 -*-
from django import forms
from sambausers.models import SambaGroup
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, HTML, Field, Fieldset
from crispy_forms.bootstrap import FormActions

from mailusers.forms import ListField

DEPARTMENTS = (
    (u'OSP', u'Отдел сопровождения проектов'),
    (u'ORGOUO', u'Отдел развития государственно-общественного управления образованием'),
    (u'OROS', u'Отдел развития образовательных систем'),
    (u'OUCHR', u'Отдел управления человеческими ресурсами'),
    (u'OM', u'Отдел маркетинга'),
    (u'IIO', u'Информационно-издательский отдел'),
    (u'ADM', u'Администрация'),
    (u'BUH', u'Бухгалтерия'),
    (u'OTHER', u'Другой'),
    )

GROUP_CHOICES = [(group.gid_number, '%s: %s' % (group.gid_number, group.description)) for group in
                 SambaGroup.objects.exclude(gid_number=513).exclude(gid_number=515)]

class SambaUserForm(forms.Form):


    full_name = forms.CharField(label=u'ФИО', help_text=u'Пупкин Василий Иванович')
    username = forms.CharField(label=u'Логин', help_text=u'pupkinvi')
    clear_password = forms.CharField(label=u'Пароль', help_text=u'минимум 5 символов')
    gecos = forms.ChoiceField(label=u'Отдел', choices=DEPARTMENTS, initial=u'OTHER', widget=forms.RadioSelect)
    mail = forms.CharField(label=u'Адрес e-mail',
                           help_text=u'pupkin@education.tomsk.ru', required=False)
    shell = forms.CharField(label=u'Shell', initial=u'/usr/local/sbin/nologin')
    mobile = forms.CharField(label=u'Номер мобильного', help_text=u'+7 XXX XXX XX XX', required=False)
    phone_number = forms.CharField(label=u'Внутренний номер', help_text=u'108')
    groups = forms.MultipleChoiceField(label=u'Дополнительные группы', choices=GROUP_CHOICES, required=False,
                                       widget=forms.CheckboxSelectMultiple)

    def __init__(self, username, *args, **kwargs):
        super(SambaUserForm, self).__init__(*args, **kwargs)
        if username:
            self.fields['clear_password'].required = False
            self.fields['clear_password'].widget.attrs['disabled'] = 'disabled'
            self.fields['username'].required = False
            self.fields['username'].widget.attrs['disabled'] = 'disabled'

        self.helper = FormHelper()
        self.helper.form_class = 'form-horizontal'
        self.helper.form_method = 'post'
        self.helper.form_action = '.'

        fields = []
        for field_name, field in self.fields.items():
            fields.append(Field(field_name, css_class='span6', placeholder=field.help_text))
            field.help_text = ''

        self.helper.layout = Layout(
            Fieldset(
                '{{title}}',
                *fields
            ),
            FormActions(
                Submit('submit', u'Сохранить', css_class='btn-primary'),
                HTML(u'<a href="{% url sambausers_index %}" class="btn">Отмена</a>'),
            )

        )


class SambaGroupForm(forms.ModelForm):
    cn = forms.CharField(label=u'Название', help_text=u'Название')
    description = forms.CharField(label=u'Описание', help_text=u'Описание')
    members = ListField(label=u'Члены группы', help_text=u'Каждый логин пользователя на новой строке')

    def __init__(self, *args, **kwargs):
#        print kwargs.pop('group_gid')
        super(SambaGroupForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_class = 'form-horizontal'
        self.helper.form_method = 'post'
        self.helper.form_action = '.'

        fields = []
        for field_name, field in self.fields.items():
            fields.append(Field(field_name, css_class='span6', placeholder=field.help_text))
            field.help_text = ''

        self.helper.layout = Layout(
            Fieldset(
                '{{title}}',
                *fields
            ),
            FormActions(
                Submit('submit', u'Сохранить', css_class='btn-primary'),
                HTML(u'<a href="{% url sambausers_index %}" class="btn">Отмена</a>'),
            )

        )

    class Meta:
        model = SambaGroup
        fields = (u'cn',
                  u'description',
                  u'members'
            )
        exclude = (u'dn', u'display_name',
                   u'gid_number',
                   u'samba_group_type',
                   u'samba_sid',
            )
