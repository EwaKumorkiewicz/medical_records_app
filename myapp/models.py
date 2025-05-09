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
    


 #modele dla użytkowników, pacjent, lekarz   
    
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models

class CustomUserManager(BaseUserManager):
    def create_user(self, email, username, date_of_birth, password=None, role=None):
        if not email:
            raise ValueError('Podaj email')
        if not username:
            raise ValueError('Podaj nazwę użytkownika')
        email = self.normalize_email(email)
        user = self.model(email=email, username=username, role=role, date_of_birth=date_of_birth)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, username, date_of_birth, password):
        user = self.create_user(email, username, date_of_birth, password, role='doctor')
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
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    date_of_birth = models.DateField()

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

