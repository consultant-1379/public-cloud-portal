from django.views.generic import TemplateView

class HomePage(TemplateView):
    template_name = 'index_billow.html'

class LoggedPage(TemplateView):
    template_name = 'base.html'

class LogoutPage(TemplateView):
    template_name = 'index_billow.html'
