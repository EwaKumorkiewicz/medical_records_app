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

#from django.contrib.auth.forms import UserCreationForm
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
    query_1 = request.GET.get('q_1')
    search_results = []

    if query or query_1:
        if query and query_1:
            search_results = CustomUser.objects.filter(
                role='patient',
                assigned_doctor__isnull=True
            ).filter(
                (Q(username__icontains=query) | Q(email__icontains=query)) & Q(pesel__icontains=query_1)
            )
        if query:
            #ci bez lekarza 
            search_results = CustomUser.objects.filter(
                role='patient',
                assigned_doctor__isnull=True
            ).filter(
                Q(username__icontains=query) | Q(email__icontains=query)
            )
        else:
            search_results = CustomUser.objects.filter(
                    role='patient',
                    assigned_doctor__isnull=True
                ).filter(
                    Q(pesel__icontains=query_1)
                )
            

    if request.method == 'POST':
        patient_id = request.POST.get('patient_id')
        patient = get_object_or_404(CustomUser, id=patient_id, role='patient')

        #przypisanie
        if patient.assigned_doctor is None:
            patient.assigned_doctor = request.user
            patient.save()

    #wyświetlanie pacjentów przypisanych do danego id_lekarza

    assigned_patients = CustomUser.objects.filter(assigned_doctor=request.user).order_by('username')

    return render(request, 'home_doctor_template.html', {
        'search_results': search_results,
        'assigned_patients': assigned_patients
    })


from .models import Wizyty
from .models import Badania 
from django.utils import timezone

from datetime import datetime, time
#pacjent_home:
@login_required
def patient_home_view(request):

    #wyświetlenie objektów tabeli Wizyty
    patient = get_object_or_404(CustomUser, id = request.user.id, role='patient')
    wizyty = Wizyty.objects.filter(patient=patient).order_by('-wizyta_data')    #TODO - zrobić model na wizyty (id lekarz, id pacjent, data, notatki, zdj?)

    badania = Badania.objects.filter(patient=patient).order_by('-badanie_data')
    now = timezone.now()

    query = request.GET.get('q')
    query_1 = request.GET.get('q_1')

    print("query:", query)
    print("query_1:", query_1)
    

    search_results = []

    parsed_date = None  

    if query_1:
        for fmt in ("%d-%m-%Y %H:%M", "%d-%m-%Y", "%Y-%m-%d"):   # na wszelki wypadek sprawdzić różne opcje
            try:
                parsed_date = datetime.strptime(query_1, fmt).date()
                break
            except ValueError:
                continue
    
    print("parsed_date:", parsed_date)

    if query and parsed_date:
        start_dt = datetime.combine(parsed_date, time.min)
        end_dt = datetime.combine(parsed_date, time.max)
        search_results = Badania.objects.filter(
            patient=patient
        ).filter(
            (Q(badanie_title__icontains=query) | Q(result_type__icontains=query)) &
            Q(badanie_data__range=(start_dt, end_dt))
        ).order_by('-badanie_data')

    elif query:
        search_results = Badania.objects.filter(
            patient = patient
        ).filter(                                
            Q(badanie_title__icontains=query) | Q(result_type__icontains = query )
        ).order_by('-badanie_data')

    elif parsed_date:
        start_dt = datetime.combine(parsed_date, time.min)
        end_dt = datetime.combine(parsed_date, time.max)
        search_results = Badania.objects.filter(
            patient=patient
        ).filter(
            Q(badanie_data__range=(start_dt, end_dt))
        ).order_by('-badanie_data')

    
    return render(request, 'home_patient_template.html', {'wizyty': wizyty, 'badania': badania, 'now': now, 'search_results': search_results})


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

    form_edit = {w.id: WizytaForm(instance=w) for w in page_obj_wizyta}


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
                                                              'page_obj_wizyta': page_obj_wizyta, 'page_obj_badanie': page_obj_badanie, 'form_edit': form_edit,})




"""
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
"""

from django.http import JsonResponse

#tu wyświetlanie chart i wartości osobno
def chart_data(request, badanie_id):
    try:

        badanie = Badania.objects.get(id = badanie_id)

        if badanie.badanie_file:
            file_path = badanie.badanie_file.path  
            
            with open(file_path, 'r') as file:
                data = []
                for line in file:
                    try:
                        data.append(float(line.strip()))
                    except ValueError:
                        continue
            
            #dane na wykres pod JSON
            chart_data = {
                'type': 'chart',
                'labels': [f'{i}' for i in range(len(data))],  
                'values': data
            }

        elif badanie.badanie_value:
            #wyswietlanie wartości
            chart_data = {
                'type': 'value',
                'value': badanie.badanie_value
            }
        
        else:
            #jeśli nic, error
            chart_data = {
                'type': 'error',
                'message': 'No data available'
            }

        return JsonResponse(chart_data)
    
    except Badania.DoesNotExist:
        return JsonResponse({'type': 'error', 'message': 'Nie znaleziono danych'}, status=404)


#usuwanie i edycja obiektów w bazie:
#wizyty:
def delete_wizyta(request, pk):
    wizyta = get_object_or_404(Wizyty, id=pk)
    if request.method == 'POST':
        wizyta.delete()
        return redirect('profil_pacjenta', wizyta.patient.id)  
    return render(request, 'myapp/confirm_delete.html', {'wizyta': wizyta})


def edit_wizyta(request, pk):
    wizyta = get_object_or_404(Wizyty, id=pk)
    if request.method == 'POST':
        form = WizytaForm(request.POST, request.FILES, instance=wizyta)
        if form.is_valid():
            form.save()
            return redirect('profil_pacjenta', wizyta.patient.id)  
    else:
        form = WizytaForm(instance=wizyta)
    return render(request, 'myapp/edit_wizyta_form.html', {'form': form, 'wizyta': wizyta})


def delete_badanie(request, pk):
    badanie = get_object_or_404(Badania, id=pk)
    if request.method == 'POST':
        badanie.delete()
        return redirect('profil_pacjenta', badanie.patient.id)  
    return render(request, 'myapp/confirm_delete.html', {'badanie': badanie})




##generowanie raportów - badania 
from django.http import HttpResponse
from django.template.loader import render_to_string
import base64
from reportlab.lib.utils import ImageReader
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image   #do formatowania pdf

import os 
from django.conf import settings
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from xml.sax.saxutils import escape


from reportlab.lib.styles import ParagraphStyle
custom_style = ParagraphStyle(
    name='CambayStyle',
    fontName='Cambay',  
    fontSize=12,
    leading=14,        
)


def generate_report(request):
    if request.method == 'POST':
        data = json.loads(request.body)
    
        badanie_title = data['badanie_title']
        result_type = data['result_type']
        badanie_data = data['badanie_data']
        notes = data['notes']
        chart_image = data.get('chart_image')
        badanie_value = data.get('badanie_value')

        #Buffer pod PDF
        buffer = BytesIO()

        doc = SimpleDocTemplate(buffer, pagesize=A4)
        content = []

        #Zachowaj formatowanie 
        notes_html = escape(notes).replace('\n', '<br>')

        #ustal font wspierający znaki polskie:
        font_path = os.path.join(settings.BASE_DIR, 'static', 'Cambay', 'Cambay-Regular.ttf')
        try:
            pdfmetrics.registerFont(TTFont('Cambay', str(font_path)))
            doc.setFont("Cambay", 12)
        except Exception as e:
            print(f"Font nie jest zaladowany: {e}")

        notes_html = escape(notes).replace('\n', '<br/>')
        
        content.append(Paragraph(f"<b>Badanie: </b> {escape(badanie_title)}", custom_style))
        content.append(Paragraph(f"<b>Typ badania: </b> {escape(result_type)}", custom_style))
        content.append(Paragraph(f"<b>Data badania: </b> {escape(badanie_data)}", custom_style))
        content.append(Spacer(1, 12))
        content.append(Paragraph("<b>Notatki: </b>", custom_style))
        content.append(Paragraph(notes_html, custom_style))
        content.append(Spacer(1, 12))

        if badanie_value:
            content.append(Paragraph(f"<b>Wynik badania: </b> {escape(badanie_value)}", custom_style))
            content.append(Spacer(1, 12))

        if chart_image:
            try:
                header, base64_data = chart_image.split(',', 1)
                image_data = base64.b64decode(base64_data)
                image_io = BytesIO(image_data)

                img = Image(image_io, width=400, height=250)
                content.append(Paragraph("<b>Wyniki badania: </b>", custom_style))
                content.append(Spacer(1, 6))
                content.append(img)

            except Exception as e:
                print("Chart image error:", e)

        
        doc.build(content)

        
        buffer.seek(0)
        response = HttpResponse(buffer, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="raport_{badanie_title}.pdf"'
        return response

    return JsonResponse({'error': 'Invalid request'}, status=400)


#generacja CSV listy pacjentów danego lekarza

import csv

def generate_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="pacjenci.csv"'

    writer = csv.writer(response)
    writer.writerow(['Imie i Nazwisko', 'PESEL', 'Data urodzenia'])

    pacjenci = CustomUser.objects.filter(assigned_doctor=request.user).order_by('username')
    for pacjent in pacjenci:
        writer.writerow([pacjent.username, pacjent.pesel, pacjent.date_of_birth])

    return response




def generate_report_wiz(request):
    if request.method == 'POST':
        data = json.loads(request.body)
    
        lekarz = data['lekarz']
        wizyta_data = data['wizyta_data']
        notes = data['notes']
        image_path = data.get('image')

        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)

        font_path = os.path.join(settings.BASE_DIR, 'static', 'Cambay', 'Cambay-Regular.ttf')
        try:
            pdfmetrics.registerFont(TTFont('Cambay', str(font_path)))
        except Exception as e:
            print(f"Font nie jest zaladowany: {e}")

        custom_style = ParagraphStyle(
            name='CambayStyle',
            fontName='Cambay',
            fontSize=12,
            leading=15,
        )

        notes_html = escape(notes).replace("\n", "<br>")

        content = []

        content.append(Paragraph(f"<b>Data wizyty:</b> {escape(wizyta_data)}", custom_style))
        content.append(Paragraph(f"<b>Lekarz:</b> {escape(lekarz)}", custom_style))
        content.append(Paragraph("<b>Notatki:</b>", custom_style))
        content.append(Paragraph(notes_html, custom_style))
        content.append(Spacer(1, 12))

        if image_path:
            abs_path = os.path.join(settings.MEDIA_ROOT, image_path.replace('/media/', ''))
            try:
                with open(abs_path, 'rb') as f:
                    content.append(Paragraph("<b>Obraz:</b>", custom_style))
                    content.append(Spacer(1, 6))
                    content.append(Image(f, width=400, height=250))
            except Exception as e:
                print('Image error:', e)

        doc.build(content)

        buffer.seek(0)
        response = HttpResponse(buffer, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="raport_{wizyta_data}.pdf"'
        return response

    return JsonResponse({'error': 'Invalid request'}, status=400)




