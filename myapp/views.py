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
    

#tutaj dodajemy widoki dla stron logowania i rejestracji:

from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect

from django.shortcuts import render, redirect
from .forms import CustomUserCreationForm

def signup_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = CustomUserCreationForm()
    return render(request, 'registration/signup.html', {'form': form})

from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm


def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            if user.role == 'doctor':
                return redirect('home_doctor')  #tu wstawimy home_page_user/home_page_doctor
            else:
                return redirect('home_user')
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()
    return render(request, 'registration/login.html', {'form': form})

def logout_view(request):
    logout(request)
    return render(request, 'registration/logged_out.html')



#redirect przez accounts/profile - automatyczna strona od django

from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required

@login_required
def profile_redirect_view(request):
    user = request.user
    if user.role == 'doctor':
        return redirect('home_doctor')  
    else:
        return redirect('home_user')    
    

##home views dla lekarz i dla user:
from .models import CustomUser
from django.shortcuts import get_object_or_404
from django.db.models import Q
#lekarz:
@login_required
def doctor_home_view(request):
    if request.user.role != 'doctor':
        return redirect('home_user')

    query = request.GET.get('q')
    search_results = []

    if query:
        # Only show unassigned patients
        search_results = CustomUser.objects.filter(
            role='patient',
            assigned_doctor__isnull=True
        ).filter(
            Q(username__icontains=query) | Q(email__icontains=query)
        )

    if request.method == 'POST':
        patient_id = request.POST.get('patient_id')
        patient = get_object_or_404(CustomUser, id=patient_id, role='patient')

        # Assign this patient to the current doctor
        if patient.assigned_doctor is None:
            patient.assigned_doctor = request.user
            patient.save()

    # Show this doctor’s assigned patients
    assigned_patients = CustomUser.objects.filter(assigned_doctor=request.user)

    return render(request, 'home_doctor_template.html', {
        'search_results': search_results,
        'assigned_patients': assigned_patients
    })
