from django import forms
from .models import Order, Client, Jdg
from django.forms.widgets import DateInput
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django.utils import timezone

class ImportForm(forms.Form):
    file = forms.FileField(label='Wybierz plik JSON')

class OrderForm(forms.ModelForm):
    order_form = forms.IntegerField(widget=forms.HiddenInput(), required=False)

    def __init__(self, *args, **kwargs):
        super(OrderForm, self).__init__(*args, **kwargs)
        
        # Ustaw domyślne wartości dla pól daty, jeśli nie zostały przekazane żadne wartości ani nie ma danych początkowych
        if not self.initial.get('date1'):
            self.initial['date1'] = timezone.now().date()
        
        # Sprawdź, czy obiekt Order jest przekazywany do formularza (dla przypadku aktualizacji)
        order_instance = kwargs.get('instance')
        if order_instance:
            # Ustaw daty z obiektu Order jako początkowe, jeśli są dostępne
            if order_instance.date1:
                self.initial['date1'] = order_instance.date1
            if order_instance.date2:
                self.initial['date2'] = order_instance.date2

    STATUS_CHOICES = (
        ("przyjeto", "Przyjęto"),
        ("wydano", "Wydano"),
        ("w realizacji", "W realizacji"),
        ("do wydania", "Do wydania"),
        ("rezygnacja z naprawy", "Rezygnacja z naprawy"),
        ("utylizacja", "Utylizacja"),
    )

    status = forms.ChoiceField(choices=STATUS_CHOICES, widget=forms.Select(attrs={'class': 'form-control'}))

    def clean_status(self):
        status = self.cleaned_data.get('status')
        date2 = self.cleaned_data.get('date2')

        if status in ['wydano', 'utylizacja', 'rezygnacja z naprawy'] and not date2:
            raise forms.ValidationError("Data zakończenia naprawy jest wymagana dla tego statusu.")
        
        return status

    class Meta:
        model = Order
        fields = ['brand', 'serial', 'date1', 'date2', 'status', 'todo', 'uwagi', 'naprawa']
        widgets = {
            'brand': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Marka sprzętu'}),
            'serial': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Numer seryjny urządzenia'}),
            'date1': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'date2': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'todo': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Zgłoszenie', 'rows': 4}),
            'uwagi': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Ewentualne uwagi', 'rows': 2}),
            'naprawa': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Co zostało zrobione'}),
        }

class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = ['client', 'phone', 'uwagi']  # Wybierz pola, które chcesz umożliwić aktualizację
        widgets = {
            'client': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Imię i Nazwisko'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Numer kontaktowy'}),
            'uwagi': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Ewentualne uwagi', 'rows': 2}),
        }

class JdgForm(forms.ModelForm):
    class Meta:
        model = Jdg
        fields = ['pole1', 'pole2', 'pole3', 'pole4']
        widgets = {
            'pole1': forms.Textarea(attrs={'rows': 3, 'cols': 40, 'maxlength': 250}),
            'pole2': forms.Textarea(attrs={'rows': 3, 'cols': 40, 'maxlength': 250}),
            'pole3': forms.Textarea(attrs={'rows': 3, 'cols': 40, 'maxlength': 250}),
            'pole4': forms.Textarea(attrs={'rows': 3, 'cols': 40, 'maxlength': 250}),
        }