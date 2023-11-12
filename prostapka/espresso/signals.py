from django.db.models.signals import post_migrate
from django.dispatch import receiver
from .models import Jdg

@receiver(post_migrate)
def create_jdg_object(sender, **kwargs):
    if Jdg.objects.count() == 0:
        Jdg.objects.create(
            pole1="Informuję, że Pana/Pani dane będą przetwarzane zgodnie z Ogólnym Rozporządzeniem w zakresie danych osobowych z dnia 27 kwietnia 2016 r.",
            pole2="Administratorem tych danych jest DANE FIRMY. Szczegółowe informacje odnośnie danych osobowych znajdują się na stronie ADRES",
            pole3="dodatkowe info",
            pole4="kontakt z serwisem: tel. XXXX tel. XXX"
        )
