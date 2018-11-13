from django.contrib.admin.views.main import ChangeList, ORDER_VAR
from django.contrib.admin import ModelAdmin


class MultiFieldSortableChangeList(ChangeList):
    """
    This class overrides the behavior of column sorting in django admin tables in order
    to allow multi field sorting


    Usage:

    class MyCustomAdmin(admin.ModelAdmin):

        ...

        def get_changelist(self, request, **kwargs):
            return MultiFieldSortableChangeList

        ...

    """

    def get_ordering(self, request, queryset):
        """
        Returns the list of ordering fields for the change list.
        First we check the get_ordering() method in model admin, then we check
        the object's default ordering. Then, any manually-specified ordering
        from the query string overrides anything. Finally, a deterministic
        order is guaranteed by ensuring the primary key is used as the last
        ordering field.
        """
        params = self.params
        ordering = list(self.model_admin.get_ordering(request)
                        or self._get_default_ordering())
        if ORDER_VAR in params:
            # Clear ordering and used params
            ordering = []
            order_params = params[ORDER_VAR].split('.')
            for p in order_params:
                try:
                    none, pfx, idx = p.rpartition('-')
                    field_name = self.list_display[int(idx)]

                    # the following 8 lines are the only ones modified by me------------------------
                    order_fields = self.get_ordering_field(field_name)
                    # I ask for __iter__ because hasattr(x, '__iter__') is true for list and tuples
                    # but false for strings
                    # http://stackoverflow.com/questions/1952464/in-python-how-do-i-determine-if-an-object-is-iterable
                    #if not hasattr(order_fields, '__iter__'):
                    if isinstance(order_fields, list) or isinstance(order_fields, tuple) or isinstance(order_fields, set):                        
                        for order_field in order_fields:
                            if order_field:
                                ordering.append(pfx + order_field)
                    else:
                        ordering.append(pfx + order_fields)

                except (IndexError, ValueError):
                    continue  # Invalid ordering specified, skip it.

        # Add the given query's ordering fields, if any.
        ordering.extend(queryset.query.order_by)

        # Ensure that the primary key is systematically present in the list of
        # ordering fields so we can guarantee a deterministic order across all
        # database backends.
        pk_name = self.lookup_opts.pk.name
        if not (set(ordering) & set(['pk', '-pk', pk_name, '-' + pk_name])):
            # The two sets do not intersect, meaning the pk isn't present. So
            # we add it.
            ordering.append('-pk')

        return ordering


class MultiFieldSortableModelAdmin(ModelAdmin):
    """
    By inherit from this class, now is possible to define admin_order_field like this:

    def user_full_name(self, obj):
        return obj.get_full_name()
    user_full_name.admin_order_field = ['first_name', 'last_name']

    """

    def get_changelist(self, request, **kwargs):
        #return SpecialOrderingChangeList
        return MultiFieldSortableChangeList
