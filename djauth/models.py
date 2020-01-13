from django.contrib.auth.models import AbstractUser #, BaseUserManager
from django.db.models.fields.related import ForeignKey
from django.utils.translation import ugettext_lazy as _
from general.models import Company
from django.db.models.deletion import CASCADE
from django.db import models
from django.core.validators import EmailValidator

#https://www.fomfus.com/articles/how-to-use-email-as-username-for-django-authentication-removing-the-username

'''
class UserManager(BaseUserManager):
    """Define a model manager for User model with no username field."""

    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        """Create and save a User with the given email and password."""
        if not email:
            raise ValueError('The given email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        """Create and save a regular User with the given email and password."""
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        """Create and save a SuperUser with the given email and password."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, password, **extra_fields)
'''

#https://docs.djangoproject.com/en/2.1/ref/contrib/admin/#django.contrib.admin.ModelAdmin.save_model



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
