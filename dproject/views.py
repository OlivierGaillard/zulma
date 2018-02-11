from django.views.generic import TemplateView
from django.conf import settings
from inventory.models import Employee


class IndexView(TemplateView):
    template_name = 'index.html'

    def get_context_data(self, **kwargs):
        context = super(IndexView, self).get_context_data(**kwargs)
        if '.prestigemikafric.com' in settings.ALLOWED_HOSTS:
            pass
        else:
            context['DEV'] = 'DEV'
        user = self.request.user
        if user.is_authenticated:
            try:
                context['employee'] = Employee.objects.get(user=user)
            except:
                context['employee'] = None
        return context
