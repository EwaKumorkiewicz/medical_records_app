from django.http import HttpResponse


def mypage1(request):
    return HttpResponse("Strona pierwsza...")

from django.shortcuts import render, redirect
from django.contrib.auth import logout
#from myapp.urls import urlpatterns

def base_redirect(request):
    logout(request)
    #return HttpResponse("Proszę zmienić adres na http://127.0.0.1:8000/myapp/accounts/login/")
    return redirect('myapp/accounts/login/')
