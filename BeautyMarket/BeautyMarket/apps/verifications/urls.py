from django.conf.urls import url
from django.contrib import admin
from . import views

urlpatterns = [
    url(r'^image_codes/(?P<uuid>[\w-]+)/$',views.ImageCodeView.as_view()),


]