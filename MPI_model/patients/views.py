from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.template import loader
from .models import patients, patient_info
from accounts.models import user
from django.contrib.auth.decorators import login_required

# Create your views here.
@login_required(login_url='accounts:user_login')
def addpatient(request):
    if request.method == 'POST':
        patient = patients()
        patient.HN = request.POST.get('HN_number')
        patient.fname = request.POST.get('firstName')
        patient.lname = request.POST.get('lastName')
        patient.gender = 0 if request.POST.get('gender') == 'male' else 1
        patient.save()
        
        pid = patients.objects.filter(HN=request.POST.get('HN_number'))[0].pid
        return HttpResponseRedirect('patientinfo/?pid='+str(pid))
    else : 
        print(request)
        template = loader.get_template('addpatient.html')
        context = {
            'user_login' : request.user.get_full_name()
        }
        return HttpResponse(template.render(context, request))

@login_required(login_url='accounts:user_login')
def patientList(request):
    print(request)
    context = {
        'list_patient': list(patients.objects.all()),
        'user_login' : request.user.get_full_name()
    }
    return render(request, 'patient_list.html', context)

@login_required(login_url='accounts:user_login')
def patientInfo(request):
    print(request)
    patient_id = int(request.GET.get('pid'))
    print("pid = " + str(patient_id))
    context = {
        'patient': patients.objects.get(pid = patient_id),
        'patient_info': list(patient_info.objects.filter(pid = patient_id)),
        'user_login' : request.user.get_full_name()
    }        
    return render(request, 'patient_info.html', context)
