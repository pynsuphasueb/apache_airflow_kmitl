from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.login_request, name="user_login"),
    url(r'^logout$', views.logout_request, name="logout"),
]