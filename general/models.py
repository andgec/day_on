import os
from ast import literal_eval
from django.db import models
from django import forms
from parler.models import TranslatableModel, TranslatedField, TranslatedFields
from shared.models import AddressMixin, ContactMixin
from django.db.models.fields.related import ForeignKey
from django.utils.translation import ugettext_lazy as _
from django.utils.html import mark_safe
from django.db.models.deletion import CASCADE, PROTECT
from django.db.models.constraints import UniqueConstraint
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from shared.utils import get_image_path
from shared.utils import imagefield_as_base64
from conf.settings import MEDIA_URL
from shared.const import VARIABLE_TYPE_CHOICES, BOOLEAN, INTEGER, DECIMAL, STRING, OPTION, MULTIPLE


class Company(AddressMixin, ContactMixin, models.Model):
    name            = models.CharField(max_length=60, unique=True, verbose_name=_('Name'))
    number          = models.CharField(max_length=30, unique=True, verbose_name=_('Number'))
    web_site        = models.CharField(max_length=250, blank=True, null=True, verbose_name=_('Website'))
    images_subdir   = 'company-logos' ## used in function get_image_path for the field "logo"
    logo            = models.ImageField(upload_to=get_image_path,
                                        blank=True,
                                        null=True,
                                        verbose_name = _('change logo'))
    domain          = models.CharField(max_length=150, unique=True, verbose_name=_('domain'))
    ## Display logo image
    def logo_tag(self):
        if self.logo:
            return mark_safe('<img src="%s" width="300") />' % os.path.join(MEDIA_URL, str(self.logo)))
        else:
            return _('not selected').capitalize()

    logo_tag.short_description = _('logo')

    def logo_base64(self):
        return imagefield_as_base64(self.logo)

    def get_config_value(self, config_key):
        try:
            value_rec = ConfigValue.objects.filter(company = self, key=config_key)[0] # Key set per company
            return value_rec.value
        except:
            try:
                cfg_key_rec = ConfigKey.objects.get(key=config_key) # Key set per system
                return cfg_key_rec.default_value()
            except:
                return ''

    class Meta:
        abstract = False
        verbose_name = _('Company')
        verbose_name_plural = _('Companies')

    def __str__(self):
        return self.name


#Base translatable class for models in Co project
class CoTranslatableModel(TranslatableModel):
    company = models.ForeignKey(Company, default=1, on_delete = PROTECT)
    class Meta:
        abstract = True


#Base class for models in Co project
class CoModel(models.Model):
    company = models.ForeignKey(Company, default=1, on_delete = PROTECT)
    class Meta:
        abstract = True


class Contact(ContactMixin, AddressMixin, models.Model):
    company     = ForeignKey(Company, default=1, on_delete=CASCADE)
    first_name  = models.CharField(max_length=60, verbose_name=_('First name'))
    last_name   = models.CharField(max_length=60, blank=True, default='', verbose_name=_('Last name'))
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    class Meta:
        verbose_name = _('Contact')
        verbose_name_plural = _('Contacts')

    def __str__(self):
        return self.first_name + ' ' + self.last_name


class Address(ContactMixin, AddressMixin, models.Model):
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    class Meta:
        abstract = False
        verbose_name = _('Address')
        verbose_name_plural = _('Addresses')
        
    def __str__(self):
        return self.address


class UnitOfMeasure(models.Model):
    company     = models.ForeignKey(Company, default=1, on_delete=CASCADE)
    name        = models.CharField(max_length=10, verbose_name=_('Name'))
    description = models.CharField(max_length=60, verbose_name=_('Description'))
    active      = models.BooleanField(default=True, verbose_name=_('Active'))
    class Meta:
        verbose_name = _('Unit of measure')
        verbose_name_plural = _('Units of measure')
    def __str__(self):
        return self.name + ' (' + self.description + ')'


class ConfigTree(TranslatableModel):
    '''
    Configuration tree to group configuration variables.
    One per system
    '''
    key         = models.SlugField(primary_key = True,
                                   max_length = 20,
                                   verbose_name = _('key')
                                   )
    parent      = models.ForeignKey("self",
                                    default = 'ROOT',
                                    db_column = 'parent_key',
                                    on_delete = PROTECT,
                                    related_name = 'values',
                                    verbose_name = _('parent'),
                                    )
    name        = TranslatedField(any_language = True)

    translations = TranslatedFields(
        name = models.CharField(max_length = 250,
                                verbose_name = _('object name'),
                                ),
    )
    
    class Meta:
        verbose_name = _('configuration tree node')
        verbose_name_plural = _('configuration tree nodes')

    def __str__(self):
        return self.name


class ConfigKey(TranslatableModel):
    '''
    Configuration setup.
    One per system.
    Holds available configuration variables.
    Records created only by migrations.
    '''
    key         = models.SlugField(primary_key = True,
                                   max_length = 20,
                                   verbose_name = _('key'),
                                   )
    node        = models.ForeignKey(ConfigTree,
                                    db_column = 'node_key',
                                    on_delete = PROTECT,
                                    related_name = 'config_keys',
                                    verbose_name = _('key node'),
                                    )
    type        = models.SmallIntegerField(default = INTEGER,
                                           choices = VARIABLE_TYPE_CHOICES,
                                           verbose_name = _('type'),
                                           )

    name        = TranslatedField(any_language = True)
    description = TranslatedField(any_language = True)
    metadata    = TranslatedField(any_language = True)

    translations = TranslatedFields(
        name        = models.CharField(max_length = 250,
                                       verbose_name = _('object name'),
                                       ),
        description = models.TextField(blank = True,
                                       null = False,
                                       default = '',
                                       verbose_name = _('description'),
                                       ),
        metadata    = models.TextField(blank = True,
                                       null = False,
                                       default = '',
                                       verbose_name = _('metadata'),
                                       ),
    )

    def default_value(self):
        metadata = self.metadata
        pos = metadata.find('#DEFAULT:')
        if pos == -1:
            return ''
        else:
            pos_endofvalue = metadata.find(',', pos, len(metadata))
            if pos_endofvalue == -1:
                pos_endofvalue = len(metadata)

            return metadata[pos+9:pos_endofvalue].strip()

    class Meta:
        verbose_name = _('configuration key')
        verbose_name_plural = _('configuration keys')

    def __str__(self):
        return self.key + ' (' + self.name + ')'


class ConfigValue(CoModel):
    '''
    Company configuration.
    One set per company.
    Records created automatically by migrations or by adding a new company through Admin pages.
    '''
    key     = models.ForeignKey(ConfigKey,
                                db_column = 'key',
                                on_delete = CASCADE,
                                related_name = 'values',
                                verbose_name = _('key'),
                                )
    value   = models.TextField(blank = True,
                               null = False,
                               default = '',
                               verbose_name = _('value')
                               )
    class Meta:
        verbose_name = _('configuration value')
        verbose_name_plural = _('configuration values')
        constraints = [
            UniqueConstraint(fields = ['company', 'key'], name='unique_company_configkey')
        ]

    def node(self):
        return self.key.node.name
    node.short_description = _('module')

    def key_name(self):
        return str(self.key.name)
    key_name.short_description = _('object name')

    def key_value(self):
        str_value = self.value.strip()
        if self.key.type in (OPTION, MULTIPLE):
            options = self._options
            if options:
                for option in options:
                    if str(option[0]).strip() == self.value.strip():
                        str_value = option[1]
            else:
                str_value = '* ERROR IN METADATA *'

        return str_value

    key_value.short_description = _('value')

    @property
    def _options(self):
        if self.key.type in (OPTION, MULTIPLE):
            mdstr = self.key.metadata
            poslb = mdstr.find('[')
            posrb = mdstr.find(']')
            if poslb > -1 and posrb > -1:
                opt_list_str = mdstr[poslb:posrb+1]
                try:
                    options = literal_eval(opt_list_str)
                except:
                    options = False
            else:
                options = False
        else:
            options = None

        return options

    @property
    def key_widget(self):
        '''
        Creating input widget for value field
        Property used on a form
        '''
        msg_wrong_metadata =  [(0, 'Incorrect or missing metadata for this configuration variable'),]
        options = self._options

        widgets = {
            BOOLEAN:    forms.RadioSelect(),
            INTEGER:    forms.NumberInput(),
            DECIMAL:    forms.NumberInput(),
            STRING:     forms.TextInput(),
            OPTION:     forms.RadioSelect(choices=msg_wrong_metadata if options == False else options),
            MULTIPLE:   forms.CheckboxSelectMultiple(choices=msg_wrong_metadata if options == False else options),
        }
        return widgets[self.key.type]

    def __str__(self):
        return  self.key_name() + ': ' + self.key_value()


# Automatically create configuration variables for newly created company.
def create_company_cfg_values(sender, instance, created=False, **kwargs):
    if created:
        for config_key in ConfigKey.objects.all():
            ConfigValue.objects.create(
                company = instance,
                key = config_key,
                value = config_key.default_value()
            )

models.signals.post_save.connect(create_company_cfg_values, sender=Company)
