from django.db import models
from django.contrib.auth.models import User
from datetime import datetime

class Client(models.Model):
    client = models.CharField(max_length=65, blank=False, null=False) #dane klienta
    phone = models.CharField(max_length=65, blank=False, null=False) #telefon kontaktowy
    uwagi = models.CharField(max_length=120, blank=True, null=True)
    is_processed = models.BooleanField(default=False)

    def __str__(self):
        return "{}".format(self.client)

# Create your models here.
class Order(models.Model):
    brand = models.CharField(max_length=50) #marka sprzętu
    serial = models.CharField(max_length=50, blank=False, null=False, default=0) #numer seryjny urządzenia
    date1 = models.DateField(blank=False, null=False) #data przyjęcia 
    date2 = models.DateField(blank=True, null=True) #data wydania
    todo = models.CharField(max_length=255) #zgłoszenie
    uwagi = models.CharField(max_length=255, blank=True, null=True) #ewentualne uwagi
    naprawa = models.CharField(max_length=255, blank=True, null=True) #co zostało zrobione
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='klient')
    empty_value_display = ''

    STATUS_CHOICES = (
        ("przyjeto", "Przyjęto"),  
        ("w realizacji", "W realizacji"),
        ("wydano", "Wydano"),
        ("do wydania", "Do wydania"),
        ("rezygnacja z naprawy", "Rezygnacja z naprawy"),
        ("utylizacja", "Utylizacja"),
    )

    status = models.CharField(max_length=64, blank=True, null=True, choices=STATUS_CHOICES)


    def __str__(self):
        return "Zamówienie nr:{} złożone w dniu {} przez klienta: {} dotyczy urządzenia nr: {}".format(self.id, self.date1, self.client, self.serial)

    def get_absolute_url(self):
        return "list"
    
class Jdg(models.Model):
    pole1 = models.CharField(max_length=150, default="Informuję, że Pana/Pani dane będą przetwarzane zgodnie z Ogólnym Rozporządzeniem w zakresie danych osobowych z dnia 27 kwietnia 2016 r.")
    pole2 = models.CharField(max_length=150, default="Administratorem tych danych jest DANE FIRMY. Szczegółowe informacje odnośnie danych osobowych znajdują się na stronie ADRES")
    pole3 = models.CharField(max_length=150, default="dodatkowe info")
    pole4 = models.CharField(max_length=150, default="kontakt z serwisem: tel. XXXX tel. XXX")
    
