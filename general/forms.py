from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from parler.forms import TranslatableModelForm

# Base class for translatable ModelForm form with validation for unique translatable name
class UniqNameTranslatableModelForm(TranslatableModelForm):
    request = None
    class Meta:
        abstract = True
        model = None

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        self.prefix = kwargs.get('prefix', None)
        super().__init__(*args, **kwargs)

    # Preventing name duplicates in any language
    def clean_name(self):
        def is_inline_duplicate(fvalue, prefix, data): # Check if there is inline with several lines with the having same name
            if not prefix:
                return False
            txtprefix = prefix[0:prefix.rfind('-') + 1]
            for key, value in data.items():
                if key != prefix + '-name' and key.find(txtprefix) != -1 and key.find('-name') != -1 and key.find('__prefix__') == -1:
                    if value == fvalue:
                        return True 
            return False

        name = self.data.get(self.prefix + '-name', None) if self.prefix else self.data.get('name', None) # Getting value from regular or inline form (with prefix)
        if not self.request or not name:
            return self.cleaned_data["name"]

        company = self.request.user.company
        obj = self.instance

        if is_inline_duplicate(name, self.prefix, self.data):
            raise ValidationError(_('You have entered a duplicate name') + ':')

        qs_duplicates = type(obj).objects.filter(
                        company = company, 
                        translations__name = name
                        ).exclude(id=obj.id or -1)
        if qs_duplicates.count() != 0:
            raise ValidationError(_('%s with this name already exists' % obj._meta.verbose_name.title().capitalize()) + '.')
        return self.cleaned_data["name"]
