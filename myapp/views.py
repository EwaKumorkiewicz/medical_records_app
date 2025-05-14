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
        #ci bez lekarza
        search_results = CustomUser.objects.filter(
            role='patient',
            assigned_doctor__isnull=True
        ).filter(
            Q(username__icontains=query) | Q(email__icontains=query)
        )

    if request.method == 'POST':
        patient_id = request.POST.get('patient_id')
        patient = get_object_or_404(CustomUser, id=patient_id, role='patient')

        #przypisanie
        if patient.assigned_doctor is None:
            patient.assigned_doctor = request.user
            patient.save()

    #wyświetlanie pacjentów przypisanych do danego id_lekarza
    assigned_patients = CustomUser.objects.filter(assigned_doctor=request.user)

    return render(request, 'home_doctor_template.html', {
        'search_results': search_results,
        'assigned_patients': assigned_patients
    })


from .models import Wizyty
from .models import Badania 
#pacjent_home:
@login_required
def patient_home_view(request):

    #wyświetlenie objektów tabeli Wizyty
    patient = get_object_or_404(CustomUser, id = request.user.id, role='patient')
    wizyty = Wizyty.objects.filter(patient=patient).order_by('-wizyta_data')    #TODO - zrobić model na wizyty (id lekarz, id pacjent, data, notatki, zdj?)

    badania = Badania.objects.filter(patient=patient).order_by('-badanie_data')
    
    return render(request, 'home_patient_template.html', {'wizyty': wizyty, 'badania': badania})


import json
from django.core.paginator import Paginator
from .forms import WizytaForm, BadaniaForm
@login_required
def patient_profile(request, pk):   #pk to argument przekazywany przez url
    #widok dla lekarza który w danej chwili obsługuje tego pacjenta
    
    patient = get_object_or_404(CustomUser, id = pk, role = 'patient')
    wizyty = Wizyty.objects.filter(patient=patient).order_by('-wizyta_data')
    badania = Badania.objects.filter(patient=patient).order_by('-badanie_data')

    paginator_wizyta = Paginator(wizyty, 5)
    paginator_badanie = Paginator(badania, 5)

    page_nr_wizyta = request.GET.get('page_1')
    page_obj_wizyta = paginator_wizyta.get_page(page_nr_wizyta)

    page_nr_badanie = request.GET.get('page_2')
    page_obj_badanie = paginator_badanie.get_page(page_nr_badanie)

    form_wizyta = WizytaForm()
    form_badanie = BadaniaForm()


    for b in badania:
        if b.badanie_file and not b.badanie_value:
            try:
                #read the file as a list of floats
                with open(b.badanie_file.path, 'r') as f:
                    values = [float(line.strip()) for line in f if line.strip()]
                
                #generate labels for x
                labels = list(range(1, len(values) + 1))

                b.chart_data = json.dumps({
                    "labels": labels,
                    "datasets": [{
                        "label": "Wyniki",
                        "data": values,
                        "borderColor": "rgb(75, 192, 192)",
                        "tension": 0.1,
                        "fill": False
                    }]
                })
            except Exception as e:
                print(f"Błąd odczytu pliku pomiaru: {e}")
                b.chart_data = json.dumps()


    if request.method == 'POST':
        if request.POST.get('submit_form') == 'wizyta':
            form_wizyta = WizytaForm(request.POST, request.FILES)
            if form_wizyta.is_valid():
                wizyta = form_wizyta.save(commit=False)
                wizyta.patient = patient
                wizyta.doctor = request.user
                wizyta.save()
                return redirect('profil_pacjenta', pk=pk)

        elif request.POST.get('submit_form') == 'badanie':
            form_badanie = BadaniaForm(request.POST, request.FILES)
            if form_badanie.is_valid():
                badanie = form_badanie.save(commit=False)
                badanie.patient = patient
                badanie.doctor = request.user
                badanie.save()
                return redirect('profil_pacjenta', pk=pk)

    return render(request, 'profil_pacjenta_template.html', {'patient': patient, 'wizyty': wizyty, 'badania': badania, 
                                                             'form_wizyta': form_wizyta, 'form_badanie': form_badanie, 
                                                              'page_obj_wizyta': page_obj_wizyta, 'page_obj_badanie': page_obj_badanie})




