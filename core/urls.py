from django.contrib import admin
from django.urls import path, include
from core import views

urlpatterns = [
    path("", views.index, name="index"),
    path("upload", views.upload, name="upload"),
    path("profile/<str:username>", views.profile, name="profile"),
    path("follow", views.follow, name="follow"),
    path("like-post", views.like_post, name="like-post"),
    path("signup", views.signup, name="signup"),
    path("signin", views.signin, name="signin"),
    path("signout", views.signout, name="signout"),
    path("setting", views.setting, name="setting"),
    path("search", views.search, name="search"),
]
