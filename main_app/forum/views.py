from django.shortcuts import render,get_object_or_404, redirect
from django.http import HttpResponse, HttpResponseRedirect,HttpResponseForbidden
from django.urls import reverse
from django.views.generic.detail import DetailView,SingleObjectMixin
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView,FormView,UpdateView,DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.db.models import Count, F, Value, Q, ObjectDoesNotExist,Sum
from .models import *
from .forms import *

# Create your views here.
def random_topic(request):
    return redirect(Topics.objects.order_by('?').first().get_absolute_url())

class SectionsListView(ListView):
    model=Sections
    template_name = 'forum/super_sections_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title']="Форум"
        return context

    def get_queryset(self):
        queryset=Sections.objects.filter(super_sections__isnull=True)
        return queryset


class SectionDetailView(SingleObjectMixin, ListView):
    paginate_by = 10
    template_name = "forum/section_detail.html"

    def get(self, request, *args, **kwargs):
        self.object = self.get_object(queryset=Sections.objects.all())
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title']=self.object.name
        context['sections']=self.object.sections_set.all()
        context['super_section']=self.object.super_sections
        context['filter_form'] = FilterForm(self.request.GET)
        return context

    def get_queryset(self):
        queryset = self.object.topics_set.all()
        queries = Q()
        filter = self.request.GET
        if ('name' in filter):
            queries &= Q(name_lower__icontains=filter['name'].lower())
        if ('author' in filter):
            queries &= Q(author__username_lower__icontains=filter['author'].lower())
        queryset = queryset.filter(queries)

        if ('order' in filter and 'sort' in filter):
            order = ''
            if (filter['order'] == 'desc'):
                order = '-'
            queryset = queryset.order_by(f'{order}{filter["sort"]}')
        return queryset


class TopicsListView(ListView):
    model=Topics
    paginate_by = 20

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title']="Все темы"
        context['filter_form'] = FilterForm(self.request.GET)
        return context

    def get_queryset(self):
        queryset=Topics.objects.prefetch_related('author')
        queries = Q()
        filter = self.request.GET
        if ('name' in filter):
            queries &= Q(name_lower__icontains=filter['name'].lower())
        if ('author' in filter):
            queries &= Q(author__username_lower__icontains=filter['author'].lower())
        queryset = queryset.filter(queries)

        if ('order' in filter and 'sort' in filter):
            order = ''
            if (filter['order'] == 'desc'):
                order = '-'
            queryset = queryset.order_by(f'{order}{filter["sort"]}')
        return queryset


class PostsListView(ListView):
    model=Posts
    paginate_by = 10

    def setup(self, request, *args, **kwargs):
        self.topic=Topics.objects.get(slug=kwargs['slug_topic'])
        if request.user.is_authenticated:
            self.forumuser=request.user.forumusers
        super(PostsListView, self).setup(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            try:
                view_statistics=Statistics.objects.get(user=self.forumuser,topics=self.topic)
            except ObjectDoesNotExist:
                view_statistics=Statistics(user=self.forumuser,value=1,content_object=self.topic)
                view_statistics.save()
        return super(PostsListView, self).get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['topic'] = self.topic
        context['super_section']=self.topic.sections
        context['rate_form']=UpdateScorePostForm

        scores={}
        for post in context['page_obj']:
            post_info={}
            score=Statistics.objects.filter(posts=post).aggregate(Sum('value'))
            post_info['score'] = score['value__sum'] if score['value__sum'] else 0
            try:
                if not self.request.user.is_authenticated:
                    raise ObjectDoesNotExist
                rate=Statistics.objects.get(user=self.forumuser,posts=post)
                rate=rate.value
            except ObjectDoesNotExist:
                rate=0
            post_info['rate']=rate
            scores[post]=post_info

        context['scores']=scores
        context['form']=CreatePostForm()
        context['can_delete_post'] = self.request.user.has_perm('posts.delete', Posts)
        context['can_delete_topic'] = self.request.user.has_perms(['topic.delete','topic.change'],Topics)

        return context

    def get_queryset(self):
        queryset=Posts.objects.prefetch_related('author').filter(topic__slug=self.topic.slug)
        queryset=queryset.order_by('post_type','time_create')
        return queryset


class PostCreateView(LoginRequiredMixin,CreateView):
    model=Posts
    form_class = CreatePostForm
    http_method_names = ['post']

    def setup(self, request, *args, **kwargs):
        self.topic=Topics.objects.get(pk=kwargs['pk'])
        self.forumuser=request.user.forumusers
        super(PostCreateView, self).setup(request, *args, **kwargs)

    def get_success_url(self):
        redirect_to=reverse('topic',kwargs={'slug_topic':self.topic.slug})
        return f'{redirect_to}?page=last#{self.object.pk}'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({'topic': self.topic,
                       'author':self.forumuser,
                       'post_type':1})
        return kwargs


class TopicCreateView(LoginRequiredMixin,CreateView):
    model=Topics
    form_class = CreateTopicForm

    def setup(self, request, *args, **kwargs):
        self.section=Sections.objects.get(slug=kwargs['slug'])
        super(TopicCreateView, self).setup(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title']='Создание темы'
        context['section']=self.section.name
        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({'section': self.section,
                       'author':self.request.user})
        return kwargs


class PostUpdateView(LoginRequiredMixin, UpdateView):
    model = Posts
    form_class = CreatePostForm
    template_name = 'forum/update_post_form.html'

    def setup(self, request, *args, **kwargs):
        self.model_post=Posts.objects.get(pk=kwargs['pk'])
        self.initial_files=AttachedFiles.objects.filter(post=self.model_post)
        self.forumuser=request.user.forumusers
        super(PostUpdateView, self).setup(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        if self.forumuser!=self.model_post.author or not self.model_post.is_editable():
            return HttpResponseForbidden()
        return super(PostUpdateView, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        response = super(PostUpdateView, self).post(request, *args, **kwargs)
        files = request.FILES.getlist('file_field')
        if 'del_initial' in request.POST:
            self.initial_files.delete()
        if files:
            not_attached_files=[]
            is_valid=True
            files_error=[]
            for file in files:
                if is_valid:
                    try:
                        attached_file = AttachedFiles(file=file, post=self.model_post)
                        attached_file.full_clean()
                        attached_file.save()
                    except ValidationError as e:
                        is_valid=False
                        files_error.append(e.message_dict['file'])
                        files_error.append(file.name)
                else:
                    not_attached_files.append(file.name)
            if not is_valid:
                files_error.append(not_attached_files)
                return self.render_to_response(self.get_context_data(attached_files_errors=files_error))

        return response

    def get_object(self):
        return self.model_post

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['attached_files_errors'] = None
        if 'attached_files_errors' in kwargs:
            context['attached_files_errors'] = kwargs['attached_files_errors']
        context['initial_files']=self.initial_files
        context['title']='Редактирование сообщения'

        return context

    def get_success_url(self):
        redirect_to=reverse('topic',kwargs={'slug_topic':self.model_post.topic.slug})
        return f'{redirect_to}?page=last#{self.model_post.pk}'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({'topic': self.model_post.topic,
                       'author': self.model_post.author,
                       'post_type': 1})
        return kwargs


class PostScoreChangeView(LoginRequiredMixin,FormView):
    form_class = UpdateScorePostForm
    http_method_names = ['post']

    def setup(self, request, *args, **kwargs):
        self.model_post=Posts.objects.get(pk=kwargs['pk'])
        self.forumuser=request.user.forumusers
        super(PostScoreChangeView, self).setup(request, *args, **kwargs)

    def form_valid(self, form):
        form.save()
        return super(PostScoreChangeView, self).form_valid(form)

    def get_success_url(self):
        redirect_to=reverse('topic',kwargs={'slug_topic':self.model_post.topic.slug})
        return f'{redirect_to}#{self.model_post.pk}'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({'post': self.model_post,
                       'forum_user':self.forumuser})
        return kwargs


class TopicDeleteView(PermissionRequiredMixin, DeleteView):
    model = Topics
    permission_required = ('topics.delete',)

    def setup(self, request, *args, **kwargs):
        super(TopicDeleteView, self).setup(request, *args, **kwargs)
        self.sections=Topics.objects.get(pk=kwargs['pk']).sections

    def get_success_url(self):
        return reverse('topics',kwargs={'slug':self.sections.slug})

    def get_context_data(self, **kwargs):
        context = super(TopicDeleteView, self).get_context_data(**kwargs)
        context['title'] = "Удалить тему"
        return context


class PostDeleteView(PermissionRequiredMixin, DeleteView):
    model = Posts
    permission_required = ('posts.delete',)

    def setup(self, request, *args, **kwargs):
        super(PostDeleteView, self).setup(request, *args, **kwargs)
        self.topic=Posts.objects.get(pk=kwargs['pk']).topic

    def get_success_url(self):
        return reverse('topic',kwargs={'slug_topic':self.topic.slug})

    def get_context_data(self, **kwargs):
        context = super(PostDeleteView, self).get_context_data(**kwargs)
        context['title'] = "Удалить сообщение"
        return context


class TopicUpdateView(PermissionRequiredMixin, UpdateView):
    model = Topics
    permission_required = ('topics.change',)
    fields = ('name','sections')
    # change default template

    def get_success_url(self):
        return reverse('topic',kwargs={'slug_topic':self.object.slug})

    def get_context_data(self, **kwargs):
        context = super(TopicUpdateView, self).get_context_data(**kwargs)
        context['title'] = "Изменить тему"
        return context