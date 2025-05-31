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
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )

    username = forms.CharField(
        label="Imię i Nazwisko",
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    date_of_birth = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        label = "Data urodzenia",

    )

    pesel = forms.CharField(
        widget=forms.TextInput(attrs= {'class': 'form-control'}),
        label = "Numer PESEL/id (11-cyfrowy)")

    password1 = forms.CharField(
        label="Hasło",
        help_text="Wprowadź bezpieczne hasło: \n " \
        "Hasło nie może zawierać twojej nazwy lub adresu email.\n" \
        "Hasło musi mieć min. 8 znaków. \n" \
        "Hasło nie może być typowe. \n" \
        "Hasło nie może składać się tylko z cyfr.",
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )

    password2 = forms.CharField(
        label="Potwierdź hasło",
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'date_of_birth', 'pesel', 'role', 'password1', 'password2')


from .models import Wizyty
from .models import Badania

class WizytaForm(forms.ModelForm):
    class Meta:
        model = Wizyty
        fields = ['wizyta_data', 'notes', 'photo']

        widgets = {
            'wizyta_data': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'photo': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }

        labels = {
            'wizyta_data': 'Data i godzina wizyty',
            'notes': 'Dodatkowe Notatki',
            'photo': 'Wstaw Zdjęcie',
        }


RESULT_TYPE_CHOICES = [
    ('HR', 'Heart Rate'),
    ('BP', 'Blood Pressure'),
    ('ECG', 'EKG'),
    ('GLU', 'Glukoza'),
    ('INNE', 'Inne'),
]

class BadaniaForm(forms.ModelForm):
    result_type = forms.ChoiceField(
        choices=RESULT_TYPE_CHOICES,
        widget=forms.RadioSelect,
        label="Typ badania"
    )


    class Meta:
        model = Badania
        fields = ['badanie_title', 'badanie_data', 'result_type', 'badanie_value', 'badanie_file', 'badanie_notatki']

        widgets = {
            'badanie_data': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'badanie_file': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'badanie_notatki': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
        }

        labels = {
            'badanie_title': 'Tytuł Wpisu',
            'badanie_data': 'Data i godzina badania',
            'badanie_notatki': 'Dodatkowe Notatki',
            'badanie_value': 'Wstaw Pomiar',
            'badanie_file': 'Lub Prześlij Plik z wartościami',
        }

    def clean(self):     #albo jedno albo drugie
        cleaned_data = super().clean()
        value = cleaned_data.get('badanie_value')
        file = cleaned_data.get('badanie_file')

        if bool(value) == bool(file):  #obydwa wypełnione lub puste
            raise forms.ValidationError("Wprowadź wartość **lub** załaduj plik.")

        return cleaned_data