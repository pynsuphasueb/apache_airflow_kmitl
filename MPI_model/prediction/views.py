from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.template import loader
from patients.models import patients, patient_info
from django.contrib.auth.decorators import login_required
import pickle

#time
import pytz
from datetime import datetime, timezone

@login_required(login_url='accounts:user_login')
def prediction(request):
    if request.method == 'POST':
        print(request)
        no = int(request.GET.get('no'))
        patient_id = patients.objects.filter(patient_info__no = no)[0].pid
        method = request.POST.get('_method')
        print(method)
        if method == 'Save' :
            CAG_confirm = request.POST.get('CAG_confirm')
            if CAG_confirm != patient_info.objects.get(no = no).CAG_confirm :
                print("Update CAG_confirm of No : " + str(no))
                print("Old : " + str(patient_info.objects.get(no = no).CAG_confirm) + " New : " + str(CAG_confirm))
                patient_info.objects.filter(no = no).update(CAG_confirm = CAG_confirm)
            context = {
            'patient': patients.objects.get(pid = patient_id),
            'patient_info': patient_info.objects.get(no = no),
            'user_login' : request.user.username
            }
            return render(request, 'prediction.html', context)
        else :
            print("Delete No : " + str(no))
            patient_info.objects.filter(no = no).delete()
            context = {
                'patient': patients.objects.get(pid = patient_id),
                'patient_info': list(patient_info.objects.filter(pid = patient_id)),
                'user_login' : request.user.username
            }
            return render(request, 'patient_info.html', context)

    else :
        utc_dt = datetime.now(timezone.utc)
        BKK = pytz.timezone('Asia/Bangkok')
        # print("BKK time   {}".patient_info.objects.filter(patient_info__no = no)[0].pid)
        
        no = int(request.GET.get('no'))
        patient_id = patients.objects.filter(patient_info__no = no)[0].pid
        date = (patient_info.objects.filter(no = no)[0].date).now().date

        print("No = " + str(no))
        print("pid = " + str(patient_id))
        context = {
            'patient': patients.objects.get(pid = patient_id),
            'date' : date,
            'patient_info': patient_info.objects.get(no = no),
            'user_login' : request.user.username
        }
        return render(request, 'prediction.html', context)

@login_required(login_url='accounts:user_login')
def addPredict(request):
    if request.method == 'POST':
        
        #time zone
        utc_dt = datetime.now(timezone.utc)
        BKK = pytz.timezone('Asia/Bangkok')
        print("BKK time   {}".format(utc_dt.astimezone(BKK).astimezone()))
        print(request)
        
        patient_id =  int(request.POST.get('pid'))
        print("Add Info pid = " + str(patient_id))
        
        patientInfo = patient_info()
        patientInfo.age = request.POST.get('age')
        patientInfo.date2 = format(utc_dt.astimezone(BKK).astimezone())
        patientInfo.BMI = request.POST.get('bmi')
        patientInfo.DM = request.POST.get('dm')
        patientInfo.HT = request.POST.get('ht')
        patientInfo.DLP = request.POST.get('dlp')
        patientInfo.CKD = request.POST.get('ckd')
        patientInfo.LAD4dmspect = request.POST.get('lad_4dmspect')
        patientInfo.LADwallthick = request.POST.get('lad_wallthick')
        patientInfo.LADwallmotion = request.POST.get('lad_wallmotion')
        patientInfo.LCX4dmspect = request.POST.get('lcx_4dmspect')
        patientInfo.LCXwallthick = request.POST.get('lcx_wallthick')
        patientInfo.LCXwallmotion = request.POST.get('lcx_wallmotion')
        patientInfo.RCA4dmspect = request.POST.get('rca_4dmspect')
        patientInfo.RCAwallthick = request.POST.get('rca_wallthick')
        patientInfo.RCAwallmotion = request.POST.get('rca_wallmotion')
        patientInfo.LVEF = request.POST.get('lvef')
        patientInfo.CAG = request.POST.get('CAG')
        patientInfo.pid = patients.objects.get(pid = patient_id)
        patientInfo.save()
        
        no = int(patient_info.objects.latest('no').no)
        return HttpResponseRedirect('/prediction?no='+str(no))
    else :
        print(request)
        patient_id =  int(request.GET.get('pid'))
        print("pid = " + str(patient_id))
        context = {
            'patient': patients.objects.get(pid = patient_id),
            'user_login' : request.user.username
        }
        return render(request, 'addprediction.html', context)

@login_required(login_url='accounts:user_login')
def predict(request):
    ls_data = [1]
    if(request.method == 'POST'):
        pid = request.POST.get('pid')
        #MPI feature 
        #LAD
        lad_4dmspect = float(request.POST.get('lad_4dmspect'))
        lad_wallthick = float(request.POST.get('lad_wallthick'))
        lad_wallmotion = float(request.POST.get('lad_wallmotion'))

        #LCX
        lcx_4dmspect = float(request.POST.get('lcx_4dmspect'))
        lcx_wallthick = float(request.POST.get('lcx_wallthick'))
        lcx_wallmotion = float(request.POST.get('lcx_wallmotion'))
        
        #RCA
        rca_4dmspect = float(request.POST.get('rca_4dmspect'))
        rca_wallthick = float(request.POST.get('rca_wallthick'))
        rca_wallmotion = float(request.POST.get('rca_wallmotion'))
        
        lvef = float(request.POST.get('lvef'))
        
        #model
        data = [lad_4dmspect, lad_wallthick, lad_wallmotion, lcx_4dmspect, lcx_wallthick, lcx_wallmotion, rca_4dmspect, rca_wallthick, rca_wallmotion, lvef]
        ls_data[0] = data
        
        #load model
        file_d = open("static/model/model_mpi", "rb")
        model = pickle.load(file_d)
        print("data :", ls_data)

        #predict
        result = model.predict(ls_data)
        print("result CAG : ", result[0])
        
        #update request
        post = request.POST.copy() # to make it mutable
        post['CAG'] = str(result[0])
        request.POST = post

        file_d.close
        addPredict(request)
        no = int(patient_info.objects.latest('no').no)
    return HttpResponseRedirect('/prediction?no='+str(no))

