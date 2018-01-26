from django.views.generic import TemplateView
from inventory.models import Employee


class IndexView(TemplateView):
    template_name = 'index.html'

    def get_context_data(self, **kwargs):
        context = super(IndexView, self).get_context_data(**kwargs)
        user = self.request.user
        if user.is_authenticated:
            try:
                context['employee'] = Employee.objects.get(user=user)
            except:
                context['employee'] = None
        return context
