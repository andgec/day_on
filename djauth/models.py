from django.contrib.auth.models import AbstractUser #, BaseUserManager
from django.db.models.fields.related import ForeignKey
from django.utils.translation import ugettext_lazy as _
from general.models import Company
from django.db.models.deletion import CASCADE
from django.db import models
from django.core.validators import EmailValidator


class User(AbstractUser):
    email_validator = EmailValidator()

    username = models.CharField(
        _('username (email address)'),
        max_length=150,
        unique=True,
        help_text=_('Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.'),
        validators=[email_validator],
        error_messages={
            'unique': _("A user with that username already exists."),
        },
    )
    email = models.EmailField(_('email address'), unique=True)
    company = ForeignKey(Company, default=1, on_delete=CASCADE, related_name='user')
    
    def is_employee(self):
        return hasattr(self, 'employee')

    is_employee.boolean = True
    is_employee.short_description = _('Employee status')

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def clean(self):
        self.username = self.__class__.objects.normalize_email(self.username)
        self.email = self.username
        super().clean()
