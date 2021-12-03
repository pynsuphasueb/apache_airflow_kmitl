from django.contrib import admin
from patients.models import patients, patient_info
# Register your models here.

admin.site.register(patients)
admin.site.register(patient_info)
