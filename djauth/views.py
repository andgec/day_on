from django.contrib.auth.views import LoginView
from .forms import CoAuthenticationForm


class CoLoginView(LoginView):
    form_class = CoAuthenticationForm
