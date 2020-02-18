import operator
from functools import reduce
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from django.db.models import UniqueConstraint, Q
from django.forms import ModelForm, ModelChoiceField
from parler.forms import TranslatableModelForm


# Base class form ModelForm with validation for unique constraints
class CoModelForm(ModelForm):
    '''
    Automatically validates unique constraints defined in related model
    '''
    request = None
    co_field = 'company'
    co_object = None

    class Meta:
        abstract = True
        model = None

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        self.co_object = self.request.user.company
        super().__init__(*args, **kwargs)
        self._limit_foreign_keys()

    def _limit_foreign_keys(self):
        # Limiting foreign key field choices to request user's company
        for field in self.fields.values():
            if hasattr(field, 'queryset') and hasattr(field.queryset.model, self.co_field):
                field.queryset = field.queryset.filter(**{self.co_field: self.co_object})

    def _get_unique_constraints(self, model_constraints):
        cons = []
        for c in model_constraints:
            if type(c) == UniqueConstraint: # Unique constraints
                con = []
                for f in c.fields:
                    if f != self.co_field:
                        con.append(f)
                if len(con) > 0:
                    cons.append(con)
        return cons if len(cons) > 0 else None

    def _get_constraint_q(self, constraint):
        '''
        Dynamically builds validation query according to unique constraints defined in related model
        '''
        q_list = [Q(**{self.co_field: self.co_object}),] # Current company only
        for field in constraint:
            cdict = {}
            value = self.data.get(field)
            cdict[field] = value
            q_list.append(Q(**cdict))
        q = type(self.instance).objects.filter(reduce(operator.and_, q_list)).exclude(id=self.instance.id or -1)
        return q

    def _validate_unique_constraint(self, constraint):
        q = self._get_constraint_q(constraint)
        if q.count() > 0:
            for field in constraint:
                if len(constraint) > 1:
                    self.add_error(field, _('%s with these values already exists') % self.instance._meta.verbose_name.title().capitalize() + '.')
                else:
                    self.add_error(field, _('%s with this value already exists') % self.instance._meta.verbose_name.title().capitalize() + '.')

    def clean(self):
        cleaned_data = super().clean()
        cons = self._get_unique_constraints(self.instance._meta.constraints)
        if cons:
            for c in cons:
                self._validate_unique_constraint(c)
        return cleaned_data


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
            '''
            raise ValidationError(
                _('{object} with this {field} already exists').format(
                    **{'object': obj._meta.verbose_name.title().capitalize(),
                       'field': _('in-p-name'),
                      }))
            '''
            raise ValidationError(_('%s with this name already exists' % obj._meta.verbose_name.title().capitalize()) + '.')
        return self.cleaned_data["name"]
