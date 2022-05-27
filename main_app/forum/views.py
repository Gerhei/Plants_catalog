from django.shortcuts import redirect
from django.http import HttpResponseForbidden, HttpResponseRedirect
from django.urls import reverse

from django.views.generic.detail import DetailView,SingleObjectMixin
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView,FormView,UpdateView,DeleteView

from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin

from django.utils.translation import gettext as _
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache


from django.db.models import Q
from .models import *
from .forms import *


def random_topic(request):
    random_topic = Topics.objects.order_by('?').first()
    return redirect(random_topic.get_absolute_url())


class SectionsListView(ListView):
    model = Sections
    template_name = 'forum/super_sections_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = _("Forum")
        context['super_title'] = _("Sections list")
        return context

    def get_queryset(self):
        queryset = Sections.objects.filter(super_sections__isnull=True)
        return queryset


@method_decorator(never_cache, name='dispatch')
class TopicsListView(SingleObjectMixin, ListView):
    """
     The combination of SingleObjectMixin and ListView allows to display object
     and at the same time use pagination for objects related to it
    """
    paginate_by = 10
    template_name = "forum/topics_list.html"

    def get(self, request, *args, **kwargs):
        try:
            self.object = self.get_object(queryset=Sections.objects.all())
        except AttributeError:
            # if the slug is not provided, then we are looking for topics from all sections
            self.object = None
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.object:
            context['title'] = self.object.name
            context['sections'] = self.object.sections_set.all()
            context['super_section'] = self.object.super_sections
        else:
            context['title'] = _("All topics")
        context['filter_form'] = FilterForm(self.request.GET)
        return context

    def get_queryset(self):
        queryset = None
        if self.object:
            queryset = self.object.topics_set.all().select_related('author__user')
        else:
            queryset = Topics.objects.select_related('author__user')

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


@method_decorator(never_cache, name='dispatch')
class TopicDetailView(SingleObjectMixin, ListView):
    """
     The combination of SingleObjectMixin and ListView allows to display object
     and at the same time use pagination for objects related to it
    """
    model = Topics
    paginate_by = 10
    template_name = "forum/topic_detail.html"

    def get(self, request, *args, **kwargs):
        self.object = self.get_object(queryset=Topics.objects.all().select_related('sections'))
        # if user is authenticated then increase topic view count
        if request.forumuser:
            content_type = ContentType.objects.get(app_label='forum', model='topics')
            # each user has only one view per topic
            Statistics.objects.get_or_create(user=request.forumuser, object_id=self.object.id,
                                             content_type=content_type, defaults={'value': 1})
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = self.object.name
        context['super_section'] = self.object.sections
        context['can_delete_post'] = self.request.user.has_perm('forum.delete_posts')
        context['can_delete_topic'] = self.request.user.has_perms(['forum.delete_topics', 'forum.change_topics'])
        context['rate_form'] = UpdateScorePostForm
        context['form'] = CreatePostForm()
        context['submit_value'] = _('Create post')
        context['enctype'] = 'multipart/form-data'
        context['action'] = reverse('create_post', kwargs={'pk': self.object.pk})


        queryset_posts_rate = Statistics.objects.filter(posts__in=context['page_obj'])\
            .values('posts', 'value')
        # get current posts rates for a given forum user
        if self.request.forumuser:
            queryset_user_rate = queryset_posts_rate.filter(user=self.request.forumuser)
            post_rate_by_user = {}
            for entry in queryset_user_rate:
                post_rate_by_user[entry['posts']] = entry['value']
            context['post_rate_by_user'] = post_rate_by_user

        # get total rate for each post
        total_post_rate = {}
        for entry in queryset_posts_rate:
            if entry['posts'] in total_post_rate:
                total_post_rate[entry['posts']] += entry['value']
            else:
                total_post_rate[entry['posts']] = entry['value']
        context['total_post_rate'] = total_post_rate

        return context

    def get_queryset(self):
        queryset = self.object.posts_set.all().select_related('author__user').\
            prefetch_related('attachedfiles_set')
        return queryset


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Posts
    form_class = CreatePostForm
    # form displaying happens in TopicDetailView, only form processing happens here
    http_method_names = ['post']

    def setup(self, request, *args, **kwargs):
        super(PostCreateView, self).setup(request, *args, **kwargs)
        self.topic = Topics.objects.get(pk=kwargs['pk'])

    def form_valid(self, form):
        self.object = form.save()
        files = self.request.FILES.getlist('attached_files')
        for file in files:
            try:
                # we don't have the ability to validate multiple files in a form
                attached_file = AttachedFiles(file=file, post=self.object)
                attached_file.full_clean()
                attached_file.save()
            except ValidationError as e:
                # TODO Somehow notify the user that his file were not added
                pass

        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        topic_url = self.topic.get_absolute_url()
        return f'{topic_url}?page=last#{self.object.pk}'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({'topic': self.topic,
                       'author': self.request.forumuser,
                       'post_type':1})
        return kwargs


@method_decorator(never_cache, name='dispatch')
class TopicCreateView(LoginRequiredMixin, CreateView):
    model = Topics
    form_class = CreateTopicForm
    template_name = 'forum/default_form_page.html'

    def setup(self, request, *args, **kwargs):
        self.section = Sections.objects.get(slug=kwargs['slug'])
        super(TopicCreateView, self).setup(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = _('Creating topic')
        context['enctype'] = 'multipart/form-data'
        context['submit_value'] = _('Create topic')
        context['change_text'] = '%s: %s.' % (_('Create a topic in the section'), self.section)

        return context

    def form_valid(self, form):
        self.object = form.save()
        post = Posts.objects.get(topic=self.object, post_type=0)
        files = self.request.FILES.getlist('attached_files')
        for file in files:
            try:
                # we don't have the ability to validate multiple files in a form
                attached_file = AttachedFiles(file=file, post=post)
                attached_file.full_clean()
                attached_file.save()
            except ValidationError as e:
                # TODO Somehow notify the user that his file were not added
                pass

        return HttpResponseRedirect(self.get_success_url())

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({'section': self.section,
                       'author': self.request.forumuser})
        return kwargs


@method_decorator(never_cache, name='dispatch')
class PostUpdateView(LoginRequiredMixin, UpdateView):
    model = Posts
    form_class = CreatePostForm
    template_name = 'forum/update_post_form.html'

    def get(self, request, *args, **kwargs):
        response = super(PostUpdateView, self).get(request, *args, **kwargs)
        if not self.object.is_user_can_edit(self.request.forumuser):
            return HttpResponseForbidden()
        return response

    def post(self, request, *args, **kwargs):
        response = super(PostUpdateView, self).post(request, *args, **kwargs)
        if not self.object.is_user_can_edit(self.request.forumuser):
            return HttpResponseForbidden()
        files = request.FILES.getlist('attached_files')
        if 'delete_initial' in request.POST:
            self.object.attachedfiles_set.all().delete()
        if files:
            is_valid = True
            not_attached_files=[]
            files_error = []
            for file in files:
                try:
                    # we don't have the ability to validate multiple files in a form
                    attached_file = AttachedFiles(file=file, post=self.object)
                    attached_file.full_clean()
                    attached_file.save()
                except ValidationError as e:
                    is_valid = False
                    files_error.append(e.message_dict['file'])
                    not_attached_files.append(file.name)
            if not is_valid:
                return self.render_to_response(self.get_context_data(attached_files_errors=files_error,
                                                                     not_attached_files=not_attached_files))

        return response

    def get_object(self):
        return Posts.objects.select_related('topic','author').\
            prefetch_related('attachedfiles_set').get(pk=self.kwargs['pk'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['attached_files_errors'] = None
        if 'attached_files_errors' in kwargs:
            context['attached_files_errors'] = kwargs['attached_files_errors']
        context['initial_files'] = self.object.attachedfiles_set.all()
        context['title'] = _('Editing post')
        context['submit_value'] = _('Edit post')
        context['enctype'] = "multipart/form-data"
        context['change_text'] = '%s: %s.' % (_('Edit a post in the topic'), self.object.topic.name)

        return context

    def get_success_url(self):
        topic_url = self.object.topic.get_absolute_url()
        return f'{topic_url}?page=last#{self.object.pk}'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({'topic': self.object.topic,
                       'author': self.object.author,
                       'post_type': 1})
        return kwargs


class PostScoreChangeView(LoginRequiredMixin, FormView):
    form_class = UpdateScorePostForm
    # only form processing happens here
    http_method_names = ['post']

    def setup(self, request, *args, **kwargs):
        self.model_post = Posts.objects.select_related('topic').get(pk=kwargs['pk'])
        super(PostScoreChangeView, self).setup(request, *args, **kwargs)

    def form_valid(self, form):
        form.save()
        return super(PostScoreChangeView, self).form_valid(form)

    def get_success_url(self):
        try:
            # take redirect url from next parameter, since it is necessary to store the page number
            success_url= f'{self.request.GET["next"]}#{self.model_post.pk}'
        except KeyError:
            success_url = f'{self.model_post.topic.get_absolute_url()}#{self.model_post.pk}'
        return success_url

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({'post': self.model_post,
                       'forum_user': self.request.forumuser})
        return kwargs


@method_decorator(never_cache, name='dispatch')
class TopicDeleteView(PermissionRequiredMixin, DeleteView):
    model = Topics
    permission_required = ('forum.delete_topics',)
    template_name = 'forum/default_form_page.html'

    def get_object(self):
        obj = Topics.objects.select_related('sections').get(pk=self.kwargs['pk'])
        return obj

    def get_success_url(self):
        return self.object.sections.get_absolute_url()

    def get_context_data(self, **kwargs):
        context = super(TopicDeleteView, self).get_context_data(**kwargs)
        context['title'] = _("Delete topic")
        context['submit_value'] = _('Delete topic')
        context['change_text'] = '%s: %s.' % (_('Delete topic in the section'), self.object.sections.name)
        context['form_message'] = '%s "%s"?' % (_('Are you sure you want to delete the topic'), self.object.name)
        return context


@method_decorator(never_cache, name='dispatch')
class PostDeleteView(PermissionRequiredMixin, DeleteView):
    model = Posts
    permission_required = ('forum.delete_posts',)
    template_name = 'forum/default_form_page.html'

    def get_object(self):
        obj = Posts.objects.select_related('topic','author__user')\
            .get(pk=self.kwargs['pk'])
        return obj

    def get_success_url(self):
        return self.object.topic.get_absolute_url()

    def get_context_data(self, **kwargs):
        context = super(PostDeleteView, self).get_context_data(**kwargs)
        context['title'] = _("Delete post")
        context['submit_value'] = _('Delete post')
        context['change_text'] = '%s: %s.' % (_('Delete a post in the topic'), self.object.topic.name)
        context['form_message'] = '%s "%s"?' % (_('Are you sure you want to delete the post'), self.object)
        return context


@method_decorator(never_cache, name='dispatch')
class TopicUpdateView(PermissionRequiredMixin, UpdateView):
    model = Topics
    permission_required = ('forum.change_topics',)
    fields = ('name', 'sections')
    template_name = 'forum/default_form_page.html'

    def get_success_url(self):
        return self.object.get_absolute_url()

    def get_context_data(self, **kwargs):
        context = super(TopicUpdateView, self).get_context_data(**kwargs)
        context['title'] = _('Change topic')
        context['submit_value'] = _('Change topic')
        context['change_text'] = '%s: %s.' % (_('Change the topic in the section'), self.object.sections.name)
        return context
