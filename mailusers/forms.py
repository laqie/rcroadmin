# coding=utf-8
from mailusers.models import MailUser

from django.forms import ModelForm, CharField, Textarea, IntegerField, TypedChoiceField
from django.core import validators

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, HTML, Field, Fieldset
from crispy_forms.bootstrap import FormActions

choises = ((1, u'Включен'),
           (0, u'Выключен'),)

class ListField(CharField):
    widget = Textarea

    def __init__(self, *args, **kwargs):
        super(ListField, self).__init__(*args, **kwargs)


    def to_python(self, value):
        value = super(ListField, self).to_python(value)
        result = []
        if value in validators.EMPTY_VALUES:
            return result
        items = value.strip().split('\n')
        for item in items:
            item = item.strip()
            if item:
                validators.validate_email(item)
                result.append(item)
        return result

    def prepare_value(self, value):
        if isinstance(value, list) or isinstance(value, tuple):
            return '\n'.join(value)
        return value


#    def widget_attrs(self, widget):
#        attrs = super(ListField, self).widget_attrs(widget)
#        attrs.update({'rows': 5})
#        if self.help_text:
#            attrs.update({'placeholder': self.help_text})
#        return attrs

class MailUserForm(ModelForm):
    first_name = CharField(label=u'Имя', help_text=u'Василий')
    last_name = CharField(label=u'Фамилия', help_text=u'Пупкин')
    full_name = CharField(label=u'Отображаемое имя', help_text=u'Пупкин Василий. Отдел 308')
    username = CharField(label=u'Логин', help_text=u'pupkinv')
    mailbox = CharField(label=u'Ящик', help_text=u'/pupkin/Maildir/')

    active = TypedChoiceField(label=u'Статус',
                              help_text=u'почтовый ящик включен?',
                              choices=choises,
                              coerce=int
    )
    email = ListField(label=u'Почтовые адреса', help_text=u'Каждый адрес на новой строке')
    alias = ListField(label=u'Почтовые псевдонимы', help_text=u'Каждый псевдоним на новой строке', required=False)

    password = CharField(label=u'Пароль', help_text=u'Минимум 6 символов', min_length=6)
    quota = IntegerField(label=u'Квота', help_text=u'Размер в байтах, 0 для выключения')


    def __init__(self, *args, **kwargs):
        super(MailUserForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_class = u'form-horizontal'
        self.helper.form_method = u'post'
        self.helper.form_action = u'.'

        fields = []
        for field_name, field in self.fields.items():
            fields.append(Field(field_name, css_class=u'span6', placeholder=field.help_text))
            field.help_text = ''
#            field.error_messages['required'] = u'Поле не заполнено'

        self.helper.layout = Layout(
            Fieldset(
                u'{{title}}',
                *fields
            ),
            FormActions(
                Submit(u'submit', u'Сохранить', css_class=u'btn-primary'),
                HTML(u'<a href="{% url mailusers_index %}" class="btn">Отмена</a>'),
            )

        )


    class Meta:
        model = MailUser
        fields = (u'first_name',
                  u'last_name',
                  u'full_name',
                  u'username',
                  u'password',
                  u'mailbox',
                  u'active',
                  u'email',
                  u'alias',
                  u'quota')
        exclude = (u'dn',)