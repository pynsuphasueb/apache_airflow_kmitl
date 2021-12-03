from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.prediction, name="predict"),
    url(r'/addpredict$', views.addPredict, name="add_predict"),
    url(r'/predict$', views.predict, name="predict_process"),
]