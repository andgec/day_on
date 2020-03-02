from django.contrib.auth.views import LoginView
from django.utils.translation import gettext_lazy as _
from .forms import CoAuthenticationForm
from general.models import Company


class CoLoginView(LoginView):
    form_class = CoAuthenticationForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = _('Log in')
        try:
            context['company'] = Company.objects.only('name').get(domain=self.request.get_host())
        except:
            context['company'] = ''
        return context
