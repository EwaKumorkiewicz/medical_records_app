from django.http import HttpResponse


def mypage1(request):
    return HttpResponse("Strona pierwsza...")


def base_redirect(request):
    return HttpResponse("Proszę zmienić adres na http://127.0.0.1:8000/myapp/accounts/login/")
