from django.conf.urls import url, include
from django.contrib import admin
from . import views

urlpatterns = [
    url(r'^qq/authorization/$',views.OAuthURLView.as_view()),
    url(r'^oauth_callback$',views.QQAuthUserView.as_view()),
]
