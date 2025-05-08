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
    
    


