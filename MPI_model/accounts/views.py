from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from accounts.models import user
from django.urls import reverse
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages

#Authen
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required

def login_request(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)
        if user:
            if user.is_active:
                login(request,user)
                return HttpResponseRedirect(reverse('patients:patient_list'))
            else:
                return HttpResponse("Your account was inactive.")
        else:
            print("Someone tried to login and failed.")
            print("They used username: {} and password: {}".format(username,password))
            # return HttpResponse("Invalid login details given")
            return render(request, 'login.html', {})
    else:
        return render(request, 'login.html', {})

@login_required(login_url='accounts:user_login')
def logout_request(request):
    logout(request)
    return HttpResponseRedirect(reverse('accounts:user_login'))