from django.views.generic import (View, ListView, DetailView,
                                  FormView, CreateView)

from django.http import JsonResponse, Http404
from django.db.models import Count
from django.shortcuts import redirect

from blog.models import Article, Like, Comment
from blog.forms import (CommentForm, CommentLikeForm, EditCommentForm,
                        DeleteCommentForm, ArticleLikeForm)


class AjaxableResponseMixin:

    def response(self, data=None):
        if data is None:
            data = {'status': 'ok'}
        return JsonResponse(data)

    def error_response(self, data=None):
        if data is None:
            data = {'status': 'ok'}
        return JsonResponse(data, status=400)


class AjaxableFormResponseMixin(AjaxableResponseMixin):
    """
        Mixin to add AJAX support to a form.
        Must be used with an object-based FormView (e.g. CreateView)
        """

    def form_invalid(self, form):
        if self.request.is_ajax():
            return super().response({'errors': form.get_errors()})
        else:
            raise Http404()

    def form_valid(self, form):
        if self.request.is_ajax():
            return super().response()
        else:
            raise Http404()


class ArticleListView(ListView):
    template_name = 'blog/index.html'
    context_object_name = 'articles'
    paginate_by = 6

    def get_queryset(self):
        # collect all articles for page
        articles = Article.objects.order_by('-pub_date').annotate(likes_count=Count('like')).all()
        # find all likes for that list
        user_likes = Like.objects.filter(article_id__in=[article.id for article in articles], user=self.request.user).\
            values_list('article_id', flat=True)
        for article in articles:
            setattr(article, 'is_liked', article.id in user_likes)

        return articles


class ArticleDetailView(DetailView):
    model = Article
    template_name = 'blog/detail.html'
    context_object_name = 'article'


class CommentsView(AjaxableResponseMixin, View):

    def get_object(self, queryset=None):
        return Comment.objects.filter(article=self.kwargs['pk']).order_by('-pub_date')

    def get(self, request, *args, **kwargs):

        return super().response(self.get_data())

    def get_data(self):
        comments = {}
        i = 0
        obj = self.get_object()
        for comment in obj:
            comments[i] = comment.as_dict(self.request)
            i = i + 1
        return {'status': 'ok',
                'comments': comments,
                'comments_count': obj.count()}


class LikesView(AjaxableResponseMixin, View):

    def get_object(self, queryset=None):
        count_likes = Article.objects.get(pk=self.kwargs['pk']).like_set.count()
        is_liked = Like.objects.filter(article=self.kwargs['pk'], user=self.request.user).exists()
        return {'count_likes': count_likes,
                'is_liked': is_liked}

    def get(self, request, *args, **kwargs):
        obj = self.get_object()
        data = {'status': 'ok',
                'count_likes': obj['count_likes'],
                'is_liked': obj['is_liked']}
        return super().response(data)


class CommentCreateView(AjaxableFormResponseMixin, CreateView):

    model = Comment
    form_class = CommentForm

    def form_valid(self, form):
        form.instance.user = self.request.user
        form.save()
        return super(CommentCreateView, self).form_valid(form)


class ArticleLikeCreateView(AjaxableFormResponseMixin, CreateView):

    model = Like
    form_class = ArticleLikeForm

    def form_valid(self, form):
        like, created = Like.objects.get_or_create(article=form.cleaned_data.get('article'), user=self.request.user)
        if not created:
            like.delete()
        return super(ArticleLikeCreateView, self).form_valid(form)


class CommentLikeCreateView(AjaxableFormResponseMixin, CreateView):

    model = Like
    form_class = CommentLikeForm

    def form_valid(self, form):
        like, created = Like.objects.get_or_create(comment=form.cleaned_data.get('comment'), user=self.request.user)
        if not created:
            like.delete()
        return super(CommentLikeCreateView, self).form_valid(form)


class CommentEditView(FormView):

    model = Comment
    template_name = 'blog/edit.html'
    context_object_name = 'comment'
    form_class = EditCommentForm

    def get_form_kwargs(self):
        kwargs = super(CommentEditView, self).get_form_kwargs()
        kwargs['comment'] = Comment.objects.filter(pk=self.kwargs.get('pk'), user=self.request.user)
        return kwargs

    def get(self, request, *args, **kwargs):
        comment = Comment.objects.filter(pk=kwargs.get('pk'), user=request.user)
        if not comment.exists():
            return redirect('blog:index')
        comment = comment.get()
        comment.article
        return self.render_to_response({'comment': comment})

    def form_valid(self, form):
        form.comment = form.comment.get()
        form.comment.content = form.cleaned_data.get('content')
        form.comment.save()

        article = Article.objects.filter(comment=form.comment)
        if article.exists():
            return redirect('blog:detail', article.get().id)
        else:
            return redirect('blog:index')

    def form_invalid(self, form):
        return self.render_to_response({'form': form, 'comment': form.comment.get()})


class CommentDelete(AjaxableFormResponseMixin, FormView):
    model = Comment
    form_class = DeleteCommentForm

    def get_form_kwargs(self):
        kwargs = super(CommentDelete, self).get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):

        form.cleaned_data.get('comment').delete()
        return super(CommentDelete, self).form_valid(form)
