from django.shortcuts import render

# Create your views here.

from django.http import HttpResponse
from django.shortcuts import render
import datetime


def mypage2(request):
    return HttpResponse("To jest myapp. widok głowny, page2")

def mysubdir1(request):
    return HttpResponse("Aplikacja myapp, widok w podkatalogu 1. MySubDir1")

def mypage3(request):
    context = {
        'napis': 'To jest napis. Text',
        'calkowita': 254,
        'rzeczywista': 193.54,
        'listaliczb': list(range(1,10)),
        'listanapisow': ['napis1', 'napis2', 'napis3'],
        'data': datetime.datetime.now(),
    }

    return render(request, 'mytemplate3.html', context)



from django.views import View
class MyClass1(View):
    def get(self, request):
        context = {
            'napis': 'To jest napis w metodzie klasy widokowej',
        }

        return render(request, 'mytemplate4.html', context)
    

from .models import MyClass2

class MyClass2View(View):
    def get(self, request):
        context = {
            'obiekty': MyClass2.objects.all()
        }

        return render(request, 'mytemplate5.html', context)
    
    


