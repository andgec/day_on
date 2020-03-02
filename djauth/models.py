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
        help_text=_('Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.'),
        validators=[email_validator],
        error_messages={
            'unique': _("A user with that username already exists."),
        },
    )
    email = models.EmailField(_('email address'))
    company = ForeignKey(Company, default=1, on_delete=CASCADE, related_name='user', verbose_name = _('Company'))

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')
        constraints = [
            models.UniqueConstraint(fields=['company', 'username'], name='company_username'),
            models.UniqueConstraint(fields=['company', 'email'], name='company_useremail'),
        ]

    def is_employee(self):
        return hasattr(self, 'employee')

    def name_or_username(self):
        return self.get_full_name() if self.get_full_name() else self.username

    is_employee.boolean = True
    is_employee.short_description = _('Employee status')

    USERNAME_FIELD = 'id'
    REQUIRED_FIELDS = []

    def clean(self):
        self.username = self.__class__.objects.normalize_email(self.username)
        self.email = self.username
        super().clean()

    def __str__(self):
        return self.username