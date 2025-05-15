from django.db import models

# Create your models here.
#tu robimy modele do obsługi danych 

class MyClass2(models.Model):
    napis = models.CharField(max_length=200)
    liczba = models.IntegerField()

    def length(self):
        return len(self.napis)
    
    def square(self):
        return self.liczba*self.liczba
    

    def __str__(self):
        return f"liczba: {self.liczba} oraz napis: {self.napis}"
    


 #modele dla użytkowników, pacjent i lekarz   
    
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.core.validators import RegexValidator

class CustomUserManager(BaseUserManager):
    def create_user(self, email, username, date_of_birth, pesel, password=None, role=None):
        if not email:
            raise ValueError('Podaj email')
        if not username:
            raise ValueError('Podaj nazwę użytkownika')
        if not pesel:
            raise ValueError('Podaj PESEL')
        email = self.normalize_email(email)
        user = self.model(email=email, username=username, role=role, date_of_birth=date_of_birth, pesel = pesel)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, username, pesel, date_of_birth, password):
        user = self.create_user(email, username, date_of_birth, pesel, password, role='doctor')
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class CustomUser(AbstractBaseUser, PermissionsMixin):
    ROLE_CHOICES = (
        ('doctor', 'Doctor'),
        ('patient', 'Patient'),
    )

    email = models.EmailField(unique=True)
    username = models.CharField(max_length=150)
    role = models.CharField(max_length = 10, choices = ROLE_CHOICES)
    date_of_birth = models.DateField()
    pesel = models.CharField(max_length = 3, validators = [RegexValidator(r'^\d{3}$', message='Wprowadź poprawny numer PESEL (3-cyfrowy).')])

    #pola z BaseUser które trzeba dodać ręcznie 
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)

    #patients link to one doctor (null at first)
    assigned_doctor = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='patients',
        limit_choices_to={'role': 'doctor'}
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'date_of_birth', 'role']

    objects = CustomUserManager()

    def __str__(self):
        return f"{self.username} ({self.role})"



##Modele na wizyty i wyniki badań:
from django.conf import settings

class Wizyty(models.Model):
    patient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='appointments_as_patient',  #tej nazwy używamy do zapytań
        limit_choices_to={'role': 'patient'}

    )
    doctor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='appointments_as_doctor',
        limit_choices_to={'role': 'doctor'}
    )

    wizyta_data = models.DateTimeField()
    photo = models.ImageField(upload_to='wizyty_photos/', blank=True, null=True)
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Appointment on {self.wizyta_data.strftime('%d-%m-%Y %H:%M')} - {self.patient.username} with {self.doctor.username}"




class Badania(models.Model):
    RESULT_TYPE_CHOICES = [
        ('HR', 'Heart Rate'),
        ('BP', 'Blood Pressure'),
        ('ECG', 'EKG'),
        ('GLU', 'Glukoza'),
        ('INNE', 'Inne'),
    ]

    patient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='lab_results_patient',
        limit_choices_to={'role': 'patient'}
    )
    doctor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,  #gdy usuniemy lekarza, to wyniki zostaną, ale pole lekarz będzie puste
        null=True,
        blank=True,
        related_name='lab_results_doctor',
        limit_choices_to={'role': 'doctor'}
    )

    badanie_title = models.CharField(max_length=50)
    result_type = models.CharField(max_length=10, choices=RESULT_TYPE_CHOICES)
    badanie_data = models.DateTimeField()

    # For simple numeric results (e.g., HR, BP, GLU)
    badanie_value = models.CharField(max_length=100, blank=True, null=True)

    # For batch files like ECG results
    badanie_file = models.FileField(upload_to='lab_results/', blank=True, null=True)

    badanie_notatki = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.result_type} - {self.patient.username} - {self.timestamp.strftime('%d-%m-%Y %H:%M')}"



