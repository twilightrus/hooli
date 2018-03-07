from django.conf.urls import url
from django.urls import path

from .views import *

app_name = "blog"

urlpatterns = [
    path('', ArticleListView.as_view(), name='index'),
    # раз уж используешь django 2.0 используй простые решения
    # url('<int:pk>/', ArticleDetailView.as_view(), name='detail'),
    url(r'^(?P<pk>[0-9]+)/$', ArticleDetailView.as_view(), name='detail'),
    url(r'^(?P<pk>[0-9]+)/comments/', CommentsView.as_view(), name='comments_get'),
    url(r'^(?P<pk>[0-9]+)/likes/', LikesView.as_view(), name='likes_get'),
    url(r'^comments/add/$', CommentCreateView.as_view(), name='comment_add'),
    url(r'^comments/(?P<pk>[0-9]+)/edit$', CommentEditView.as_view(), name='comment_edit'),
    url(r'^comments/delete/$', CommentDelete.as_view(), name='comment_delete'),
    url(r'^likes/articles/add/$', ArticleLikeCreateView.as_view(), name='like_article_add'),
    url(r'^likes/comments/add/$', CommentLikeCreateView.as_view(), name='like_comment_add'),
    ]
