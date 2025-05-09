from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser

class CustomUserCreationForm(UserCreationForm):
    ROLE_CHOICES = (
        ('doctor', 'Jestem Lekarzem'),
        ('patient', 'Jestem Pacjentem'),
    )

    role = forms.ChoiceField(choices=ROLE_CHOICES, widget=forms.RadioSelect, label="Rola")

    email = forms.EmailField(
        label="Podaj email",
    )

    username = forms.CharField(
        label="Imię i Nazwisko"
    )

    date_of_birth = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        label = "Data urodzenia",

    )

    password1 = forms.CharField(
        label="Hasło",
        help_text="Wprowadź bezpieczne hasło: \n " \
        "Hasło nie może zawierać twojej nazwy lub adresu email.\n" \
        "Hasło musi mieć min. 8 znaków. \n" \
        "Hasło nie może być typowe. \n" \
        "Hasło nie może składać się tylko z cyfr.",
        widget=forms.PasswordInput
    )

    password2 = forms.CharField(
        label="Potwierdź hasło",
        widget=forms.PasswordInput
    )

    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'date_of_birth', 'role', 'password1', 'password2')