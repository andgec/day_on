from django.contrib import admin
from parler.admin import TranslatableAdmin, TranslatableTabularInline
from parler.forms import TranslatableBaseInlineFormSet
from django.utils.translation import ugettext_lazy as _
from co_manager.admin import admin_site
from .models import Company, UnitOfMeasure
from .forms import CoModelForm
from shared.utils import field_exists

class CompanyAdmin(admin.ModelAdmin):
    def get_queryset(self, request):
        qs=super().get_queryset(request)
        if request.user.is_superuser:
            return qs.exclude(id=1)
        return qs.filter(id=request.user.company.id)

    def has_add_permission(self, request, obj=None):
        return request.user.is_superuser

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser

    fieldsets = (
        (None, {
            'fields': ('name', 'number')
        }),
        (_('Address'), {
            'fields': ('address', 'city', 'post_code', 'country')
        }),
        (_('Contact information'), {
            'fields': ('email', 'phone_no', 'mobile_no', 'fax_no')
        }),
        (_('Other'), {
            'fields': ('web_site', 'logo_tag', 'logo', 'logo_base64')
        }),
    )

    readonly_fields = ('logo_tag', 'logo_base64')


# Base class to exchange ModelAdmin
class CoModelAdmin(admin.ModelAdmin):
    form = CoModelForm
    exclude = ('company',)
    def get_queryset(self, request):
        qs=super().get_queryset(request)
        return qs.filter(company = request.user.company)

    def save_model(self, request, obj, form, change):
        obj.company = request.user.company
        super().save_model(request, obj, form, change)

    def get_form(self, request, obj=None, change=False, **kwargs):
        AdminForm = super().get_form(request, obj, **kwargs)
        class AdminFormWithRequest(AdminForm):
            def __new__(cls, *args, **kwargs):
                kwargs['request'] = request
                return AdminForm(*args, **kwargs)
        return AdminFormWithRequest

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        qs = db_field.related_model.objects.filter(company = request.user.company)
        if field_exists(db_field.related_model, 'name'):
            qs = qs.order_by('name')
        else:
            qs = qs.order_by('id')
        kwargs['queryset'] = qs
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        qs = kwargs.get('queryset', None)
        if not qs:
            if field_exists(db_field.related_model, 'company'):
                qs = db_field.related_model.objects.filter(company = request.user.company)
            else:
                qs = db_field.related_model.objects.all()
        kwargs['queryset'] = qs
        return super().formfield_for_manytomany(db_field, request, **kwargs)

    def save_formset(self, request, form, formset, change):
        # Setting company for inlines (from current user)
        instances = formset.save(commit=False)
        for obj in formset.deleted_objects:
            obj.delete()
        for instance in instances:
            if hasattr(instance, 'company'):
                instance.company = request.user.company
            instance.save()
        formset.save_m2m()


# Base class to exchange TranslatableModelAdmin
class CoTranslatableAdmin(TranslatableAdmin):
    exclude = ('company',)

    def get_queryset(self, request):
        qs=super().get_queryset(request)
        return qs.filter(company = request.user.company).prefetch_related('translations')

    def save_model(self, request, obj, form, change):
        obj.company = request.user.company
        super().save_model(request, obj, form, change)

    def get_form(self, request, obj=None, **kwargs):
        AdminForm = super().get_form(request, obj, **kwargs)
        class AdminFormWithRequest(AdminForm):
            def __new__(cls, *args, **kwargs):
                kwargs['request'] = request
                return AdminForm(*args, **kwargs)
        return AdminFormWithRequest

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if field_exists(db_field.related_model, 'company'):
            qs = db_field.related_model.objects.filter(company = request.user.company)
        else:
            qs = db_field.related_model.objects.all()
        kwargs['queryset'] = qs
        return super().formfield_for_manytomany(db_field, request, **kwargs)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        qsb = db_field.related_model.objects.filter(company = request.user.company)
        if field_exists(db_field.related_model, 'translations'):
            qs = qsb.active_translations().only('id').prefetch_related('translations')
        elif field_exists(db_field.related_model, 'name'):
            qs = qsb.order_by('name')
        else:
            qs = qsb.order_by('id')
        kwargs['queryset'] = qs
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def save_formset(self, request, form, formset, change):
        # Setting company for inlines (from current user)
        instances = formset.save(commit=False)
        for obj in formset.deleted_objects:
            obj.delete()
        for instance in instances:
            if hasattr(instance, 'company'):
                instance.company = request.user.company
            instance.save()
        formset.save_m2m()


# Base class for Translatable Inline FormSet
class CoTranslatableInlineFormSet(TranslatableBaseInlineFormSet):
    def _construct_form(self, i, **kwargs):
        kwargs['request'] = self.request
        form = super()._construct_form(i, **kwargs)
        return form


# Base class for Translatable Tabular InLine
class CoTranslatableTabularInline(TranslatableTabularInline):
    formset = CoTranslatableInlineFormSet

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        qs = db_field.related_model.objects.filter(company = request.user.company)
        if field_exists(db_field.related_model, 'translations'):
            qs = qs.translated().order_by('translations__name')
        elif field_exists(db_field.related_model, 'name'):
            qs = qs.order_by('name')
        else:
            qs = qs.order_by('id')
        kwargs['queryset'] = qs
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def get_formset(self, request, obj=None, **kwargs):
        formset = super().get_formset(request, obj, **kwargs)
        formset.request = request
        return formset


admin_site.register(Company, CompanyAdmin)
admin_site.register(UnitOfMeasure, CoModelAdmin)