from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.patientList, name="patient_list"),
    url(r'^/addpatient$', views.addpatient, name="add_patient"),
    url(r'^/patientinfo/$', views.patientInfo, name="patient_info"),
]