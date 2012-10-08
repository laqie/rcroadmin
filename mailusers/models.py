from ldapdb.models.fields import CharField, IntegerField, ListField
import ldapdb.models

class MailUser(ldapdb.models.Model):
    base_dn = 'ou=mailusers,dc=education,dc=tomsk,dc=ru'
    object_classes = ['top', 'inetOrgPerson', 'mailUser']

    first_name = CharField(db_column='givenName', default='Name')
    last_name = CharField(db_column='sn', default='Surname')
    full_name = CharField(db_column='cn', default='Surname Name')
    email = ListField(db_column='mail')
    username = CharField(db_column='uid', primary_key=True)
    mailbox = CharField(db_column='mailbox')
    active = IntegerField(db_column='mailboxActive', default=1)
    password = CharField(db_column='clearPassword')
    quota = CharField(db_column='quota', default='0')
    alias = ListField(db_column='maildrop')

    def __unicode__(self):
        return '%s :: %s ' % (self.username, self.email)
