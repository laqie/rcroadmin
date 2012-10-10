# coding=utf-8
from ldapdb.models.fields import CharField, IntegerField, ListField
import ldapdb.models

from django.conf import settings
from django.db import connections, router
import ldap
import smbpasswd
import hashlib
import base64
import time

get_base64_md5 = lambda password: base64.standard_b64encode(hashlib.md5(password).digest())

DEPARTMENTS = (
    (u'OSP', u'Отдел сопровождения проектов'),
    (u'ORGOUO', u'Отдел развития государственно-общественного управления образованием'),
    (u'OGO', u'Отдел развития государственно-общественного управления образованием'),
    (u'OROS', u'Отдел развития образовательных систем'),
    (u'OUCHR', u'Отдел управления человеческими ресурсами'),
    (u'OUCR', u'Отдел управления человеческими ресурсами'),
    (u'OMAS', u'Отдел мониторинга, аналитики и статистики'),
    (u'OM', u'Отдел маркетинга'),
    (u'IOO', u'Информационно-издательский отдел'),
    (u'IIO', u'Информационно-издательский отдел'),
    (u'ADM', u'Администрация'),
    (u'BUH', u'Бухгалтерия'),
    (u'OIT', u'Отдел информационных технологий'),
    (u'OTHER', u'Другой'),
    (u'OS', u'Другой'),
    )

def get_domain_info():
    db = router.db_for_write(ldapdb.models.Model)
    connection = connections[db]
    data = connection.search_s(
        settings.BASE_DN,
        ldap.SCOPE_SUBTREE,
        filterstr='sambaDomainName=%s' % settings.DOMAIN)

    if len(data):
        domain_dn, domain_info = data[0]
        domain_sid = domain_info.get('sambaSID', None)[0]
        domain_next_uid = domain_info.get('uidNumber', None)[0]
        domain_last_rid = domain_info.get('sambaNextRid', None)[0]

        return domain_dn, domain_sid, domain_next_uid, domain_last_rid

    return None


def increase_samba_rid():
    data = get_domain_info()

    if data:
        domain_dn, domain_sid, domain_next_uid, domain_last_rid = data
        uid = str(int(domain_next_uid) + 1)
        rid = str(int(domain_last_rid) + 1)

        db = router.db_for_write(ldapdb.models.Model)
        connection = connections[db]

        modlist = [
            (ldap.MOD_REPLACE, 'uidNumber', [uid]),
            (ldap.MOD_REPLACE, 'sambaNextRid', [rid])]

        connection.modify_s(domain_dn, modlist)

        return True

    return False


def create_or_change_user(username,
                          full_name=None,
                          gecos=None,
                          clear_password=None,
                          mail=None,
                          phone_number=None,
                          mobile=None,
                          shell=None,
                          *args, **kwargs):
    user = SambaUser.objects.filter(username=username)
    if user:
        user, create = user[0], False
    else:
        user, create = SambaUser(), True

    if not create:
        if full_name:
            user.change_full_name(full_name)
        if clear_password:
            user.change_password(clear_password)

        user.gecos = gecos if gecos else user.gecos
        user.mail = [mail] if mail else user.mail
        user.phone = phone_number if phone_number else user.phone
        user.mobile = mobile if mobile else user.mobile
        user.login_shell = shell if shell else user.login_shell
        user.save()

    else:
        _, domain_sid, domain_next_uid, domain_last_rid = get_domain_info()
        never = 2147483647

        user.username = username
        user.cn = username
        user.given_name = ' '.join(full_name.split(' ')[1:])
        user.display_name = ' '.join(
            (full_name.split(' ')[0], '%s.' % full_name.split(' ')[1][0], '%s.' % full_name.split(' ')[2][0]))
        user.last_name = full_name.split(' ')[0]
        user.uid_number = int(domain_next_uid)
        user.gid_number = 513
        user.home_dir = u'/home/%s/' % username
        user.login_shell = shell
        user.gecos = gecos
        user.mail = [mail]

        user.organization = u'РЦРО'
        user.city = u'Томск'
        user.mobile = mobile
        user.phone = phone_number

        user.shadow_last_change = int(time.time())
        user.shadow_max = 900

        user.samba_pwd_last_set = int(time.time())
        user.samba_pwd_can_change = 0
        user.samba_pwd_must_change = never
        user.samba_logon_time = 0
        user.samba_logoff_time = never
        user.samba_kickoff_time = never
        user.samba_acct_flags = u'[UX]'
        user.samba_sid = '%s-%s' % (domain_sid, int(domain_last_rid) + 1)
        user.samba_home_path = r'\\%s\%s' % (settings.SERVER_NAME, username)

        user.samba_nt_password = smbpasswd.hash(clear_password)[1]
        user.user_password = u'{MD5}' + get_base64_md5(clear_password)
        user.save()
        increase_samba_rid()

    return user


class SambaGroup(ldapdb.models.Model):
    base_dn = 'ou=groups,dc=education,dc=tomsk,dc=ru'

    object_classes = [
        'top',
        'posixGroup',
        'sambaGroupMapping',
    ]

    cn = CharField(db_column='cn', primary_key=True)
    description = CharField(db_column='description')
    display_name = CharField(db_column='displayName')
    gid_number = IntegerField(db_column='gidNumber', unique=True)

    members = ListField(db_column='memberUid', unique=False)

    samba_group_type = IntegerField(db_column='sambaGroupType', default=2)
    samba_sid = CharField(db_column='sambaSID', unique=True)


    def get_members(self):
        return [SambaUser.objects.get(username=user) for user in self.members]

    def remove_member(self, username):
        self.members = [member for member in self.members if member != username]
        self.save()

    def add_member(self, username):
        if username not in self.members:
            self.members.append(username)
            self.save()
            return True
        return False


    @classmethod
    def get_last_gid(cls):
        return cls.objects.order_by('-gid_number')[0].gid_number

    def __unicode__(self):
        return '%s: %s' % (self.gid_number, self.description)


    class Meta:
        ordering = ['gid_number']


class SambaUser(ldapdb.models.Model):
    base_dn = 'ou=users,dc=education,dc=tomsk,dc=ru'

    object_classes = [
        'top',
        'person',
        'organizationalPerson',
        'posixAccount',
        'shadowAccount',
        'inetOrgPerson',
        'sambaSamAccount',
    ]

    username = CharField(db_column='uid', primary_key=True)
    cn = CharField(db_column='cn', unique=True)
    given_name = CharField(db_column='givenName')
    display_name = CharField(db_column='displayName')
    last_name = CharField(db_column='sn')
    uid_number = IntegerField(db_column='uidNumber', unique=True)
    gid_number = IntegerField(db_column='gidNumber', default=513)
    home_dir = CharField(db_column='homeDirectory')
    login_shell = CharField(db_column='loginShell')
    gecos = CharField(db_column='gecos', choices=DEPARTMENTS, max_length=5, default=u'OTHER')
    mail = ListField(db_column='mail')

    organization = CharField(db_column='o')
    city = CharField(db_column='l')
    mobile = CharField(db_column='mobile')
    phone = CharField(db_column='telephoneNumber')

    shadow_last_change = IntegerField(db_column='shadowLastChange')
    shadow_max = IntegerField(db_column='shadowMax', default=900)

    samba_pwd_last_set = IntegerField(db_column='sambaPwdLastSet', default=0)
    samba_pwd_can_change = IntegerField(db_column='sambaPwdCanChange', default=0)
    samba_pwd_must_change = IntegerField(db_column='sambaPwdMustChange', default=0)
    samba_logon_time = IntegerField(db_column='sambaLogonTime', default=0)
    samba_logoff_time = IntegerField(db_column='sambaLogoffTime', default=0)
    samba_kickoff_time = IntegerField(db_column='sambaKickoffTime', default=0)
    samba_acct_flags = CharField(db_column='sambaAcctFlags', default=u'[UX]')
    samba_sid = CharField(db_column='sambaSID')
    samba_home_path = CharField(db_column='sambaHomePath')

    samba_nt_password = CharField(db_column='sambaNTPassword')

    user_password = CharField(db_column='userPassword')


    def change_password(self, new_password):
        self.samba_nt_password = smbpasswd.hash(new_password)[1]
        self.user_password = u'{MD5}' + get_base64_md5(new_password)
        self.samba_pwd_last_set = int(time.time())
        self.shadow_last_change = int(time.time())
        self.samba_pwd_must_change = 2147483647


    def change_full_name(self, full_name):
        if len(full_name.split()) == 3:
            self.given_name = ' '.join(full_name.split(' ')[1:])
            self.display_name = ' '.join(
                (full_name.split(' ')[0], '%s.' % full_name.split(' ')[1][0], '%s.' % full_name.split(' ')[2][0]))
            self.last_name = full_name.split(' ')[0]
            return True
        else:
            return False


    @property
    def primary_group(self):
        return SambaGroup.objects.get(gid_number=self.gid_number)

    @property
    def user_groups(self):
        return SambaGroup.objects.filter(members__contains=self.username)

    @property
    def user_groups_gids(self):
        return [group.gid_number for group in
                SambaGroup.objects.exclude(gid_number__in=[513, 515]).filter(members__contains=self.username)]

    def __unicode__(self):
        return "%s: %s" % (self.uid_number, self.username)


    class Meta:
        ordering = ['username']