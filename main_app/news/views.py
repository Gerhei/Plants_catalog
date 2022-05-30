from django.shortcuts import redirect
from django.views.generic import ListView
from django.views.generic.edit import FormMixin
from django.views.generic.detail import SingleObjectMixin
from django.db.models import Q
from django.utils.translation import gettext as _
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache

from .models import *
from .forms import *


def random_news(request):
    return redirect(News.objects.order_by('?').first().get_absolute_url())


class NewsListView(ListView):
    model = News
    paginate_by =  20

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = _("News List")
        context['filter_form'] = FilterForm(self.request.GET)
        return context

    def get_queryset(self):
        queryset = News.objects.filter(is_published=True)
        queries = Q()
        filter = self.request.GET
        if ('title' in filter):
            queries &= Q(title_lower__icontains=filter['title'].lower())
        if 'publication_date_year' in filter and filter['publication_date_year']:
            queries &= Q(publication_date__year=filter['publication_date_year'])
        if 'publication_date_month' in filter and filter['publication_date_month']:
            queries &= Q(publication_date__month=filter['publication_date_month'])
        if 'publication_date_day' in filter and filter['publication_date_day']:
            queries &= Q(publication_date__day=filter['publication_date_day'])


        queryset = queryset.filter(queries)

        if ('order' in filter and 'sort' in filter):
            order = ''
            if (filter['order'] == 'desc'):
                order = '-'
            queryset = queryset.order_by(f'{order}{filter["sort"]}')
        return queryset


@method_decorator(never_cache, name='dispatch')
class NewsDetailView(FormMixin, SingleObjectMixin, ListView):
    """
     The combination of SingleObjectMixin and ListView allows to display object
     and at the same time use pagination for objects related to it.
     FormMixin also allows to show and process the form on the same page.
    """
    paginate_by = 10
    template_name = "news/news_detail.html"
    form_class = CreateCommentForm

    def setup(self, request, *args, **kwargs):
        super(NewsDetailView, self).setup(request, *args, **kwargs)
        self.object = self.get_object(queryset=News.objects.filter(is_published=True))
        self.object_list = self.get_queryset()

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = context['object'].title
        context['action'] = reverse('detailed_news', kwargs={'slug': self.object.slug})
        context['submit_value'] = _('Create comment')
        return context

    def get_queryset(self):
        queryset = Comments.objects.filter(news=self.object).select_related('user', 'user__forumusers')
        return queryset

    def get_success_url(self):
        return f'{self.object.get_absolute_url()}?page=last#comments'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({'news': self.object,
                       'user': self.request.user})
        return kwargs

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)
