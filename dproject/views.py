from django.views.generic import TemplateView
from django.conf import settings
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from inventory.models import Employee, Article


class IndexView(TemplateView):
    template_name = 'index.html'

    def get_context_data(self, **kwargs):
        context = super(IndexView, self).get_context_data(**kwargs)
        if '.prestigemikafric.com' in settings.ALLOWED_HOSTS:
            pass
        else:
            context['DEV'] = 'DEV'


        articles_en_soldes = Article.objects.filter(solde='S')
        paginator = Paginator(articles_en_soldes, 15)
        page = self.request.GET.get('page')
        start_index = 1
        try:
            articles = paginator.page(page)
            start_index = articles.start_index()
        except PageNotAnInteger:
            articles = paginator.page(1)
        except EmptyPage:
            articles = paginator.page(paginator.num_pages)  # last page
            start_index = articles.start_index()
        context['soldes'] = articles
        context['count'] =  articles_en_soldes.count()
        context['start_index'] = start_index

        user = self.request.user
        if user.is_authenticated:
            try:
                context['employee'] = Employee.objects.get(user=user)
            except:
                context['employee'] = None
        return context


