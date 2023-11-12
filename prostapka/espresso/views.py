from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from .models import Order, Client, Jdg
from datetime import datetime, date, timedelta
from django.views.generic import ListView, UpdateView, CreateView, DeleteView, View, TemplateView
from django.urls import reverse_lazy
import json
from django.db.models import Q, Min
from .forms import ImportForm, OrderForm, ClientForm, JdgForm
from django.core.paginator import (
    Paginator,
    EmptyPage,
    PageNotAnInteger,
)
from django.core.serializers import serialize
from django.contrib import messages
import hashlib
from .confirm import confirm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import transaction


# LOGOWANIE
def login_user(request):
    error_message = None  # Utwórz zmienną na ewentualny komunikat o błędzie

    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            error_message = "Nieprawidłowe dane logowania."
            messages.error(request, error_message)  

    return render(request, 'login.html', {'error_message': error_message})

def logout_user(request):
    logout(request)
    messages.success(request, 'Zostałeś wylogowany. Zaloguj się ponownie, jeśli chcesz kontynuować.')
    return redirect('login')

# WYŚWIETLANIE 
@login_required(login_url='login')
def home(request):
    liczba_przyjetych = Order.objects.filter(status="przyjeto").count()
    liczba_napraw = Order.objects.filter(status='w realizacji').count()
    liczba_dowydania = Order.objects.filter(status='do wydania').count()

    aktualny_dzien = date.today()

    # Ilość zlecen w tym miesiącu
    aktualny_miesiac = date.today().month
    ilosc_napraw_miesiac = Order.objects.filter(date2__month=aktualny_miesiac).count()
    liczba_przyjetych_miesiac = Order.objects.filter(date1__month=aktualny_miesiac).count()

    # Ilość zleceń w tym roku
    aktualny_rok = date.today().year
    ilosc_napraw_rok = Order.objects.filter(date2__year=aktualny_rok).count()

    return render(request, 'home.html', {
        'liczba_napraw': liczba_napraw,
        'liczba_dowydania': liczba_dowydania,
        'liczba_przyjetych': liczba_przyjetych,
        'liczba_przyjetych_miesiac': liczba_przyjetych_miesiac,
        'aktualny_dzien': aktualny_dzien,
        'ilosc_napraw_miesiac': ilosc_napraw_miesiac,
        'ilosc_napraw_rok': ilosc_napraw_rok,
    })

@login_required(login_url='login')
def detail_order(request, client_id=None):
    client = get_object_or_404(Client, id=client_id)
    orders = Order.objects.filter(client=client).order_by('-id')  # Pobierz wszystkie zamówienia powiązane z klientem
    context = {'client': client, 'orders': orders}  # Przekaz QuerySet do kontekstu

    return render(request, 'order_detail.html', context)

class ListaNaprawView(LoginRequiredMixin, ListView):
    model = Order
    template_name = 'order_list.html'
    context_object_name = 'order'
    ordering = ['-id']
    paginate_by = 20
    login_url = '/login/' 

    def get_queryset(self):
        status = self.request.GET.get('status')
        if status == 'w_realizacji':
            return Order.objects.filter(status="w realizacji").order_by('-id')
        elif status == 'utylizacja':
            return Order.objects.filter(status="utylizacja").order_by('-id')
        elif status == 'przyjeto':
            return Order.objects.filter(status="przyjeto").order_by('-id')        
        elif status == 'do wydania':
            return Order.objects.filter(status="do wydania").order_by('-id')
        elif status == 'rezygnacja z naprawy':
            return Order.objects.filter(status="rezygnacja z naprawy").order_by('-id')        
        else:
            return Order.objects.all().order_by('-id')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        status = self.request.GET.get('status')
        status_title = ""
        if status == 'w_realizacji':
            status_title = "W realizacji"
        elif status == 'utylizacja':
            status_title = "Utylizacja"
        elif status == 'przyjeto':
            status_title = "Przyjęto"
        elif status == 'do wydania':
            status_title = "Do wydania"
        elif status == 'rezygnacja z naprawy':
            status_title = "Rezygnacja z naprawy"
        else:
            status_title = "Wszystkie naprawy"

        default_page = 1
        page = self.request.GET.get('page', default_page)
        items = self.get_queryset()
        items_per_page = 20
        paginator = Paginator(items, items_per_page)

        try:
            items_page = paginator.page(page)
        except PageNotAnInteger:
            items_page = paginator.page(default_page)
        except EmptyPage:
            items_page = paginator.page(paginator.num_pages)

        context["items_page"] = items_page
        context["status_title"] = status_title  # Dodaj nowy klucz do kontekstu
        return context

class ListaKlientowView(LoginRequiredMixin, ListView):
    model = Client
    template_name = 'client_list.html'
    context_object_name = 'clients'
    ordering = ['-id']
    paginate_by = 20
    login_url = '/login/' 

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        items = Client.objects.all().order_by('-id')
        paginator = Paginator(items, self.paginate_by)

        page = self.request.GET.get('page')
        clients = paginator.get_page(page)

        context['clients'] = clients
        return context
    
# --------------- TWORZENIE I EDYCJA REKORDÓW --------------------
@login_required(login_url='login')
def create_or_get_client(request):
    if request.method == 'POST':
        form = ClientForm(request.POST)
        if form.is_valid():
            client_data = {
                'client': form.cleaned_data['client'],
                'phone': form.cleaned_data['phone'],
                'uwagi': form.cleaned_data['uwagi'],
            }

            # Sprawdź, czy klient już istnieje w bazie danych (jeśli klient istnieje, nawet jeśli tylko jedno z pól pasuje, zwróci obiekt klienta)
            existing_client = Client.objects.filter(Q(client=client_data['client']) | Q(phone=client_data['phone'])).first()

            if existing_client:
                # Jeśli klient istnieje, przekazujemy dane klienta do szablonu
                client_form = ClientForm(initial=client_data)  # Utwórz formularz z początkowymi danymi klienta
                return render(request, 'confirm_existing_client.html', {'existing_client': existing_client, 'client_form': client_form})

            # Jeśli klient nie istnieje, utwórz nowego klienta z hashami
            new_client = Client.objects.create(
                client=client_data['client'],
                phone=client_data['phone'],
                uwagi=client_data['uwagi']
            )

            # Tutaj możesz przekierować użytkownika gdzie chcesz, np. do formularza tworzenia zamówienia dla nowego klienta
            return redirect('order_create', client_id=new_client.id)

    else:
        form = ClientForm()

    return render(request, 'client.html', {'form': form})

@login_required(login_url='login')
def create_client(request):
    # Tworzymy nowego klienta bez sprawdzania poprawności danych
    new_client = Client.objects.create(client='Nowy Klient', phone='Nowy Telefon', uwagi='Nowe Uwagi')
    # Przekierowujemy od razu do formularza tworzenia zamówienia dla nowego klienta
    return redirect('order_create', client_id=new_client.id)

class ClientDeleteView(LoginRequiredMixin, DeleteView):
    model = Client
    template_name = 'client_confirm_delete.html'  # Stwórz odpowiedni szablon potwierdzający usunięcie klienta
    success_url = reverse_lazy('client_list')  # Przekieruj użytkownika po usunięciu klienta

class OrderCreate(LoginRequiredMixin, CreateView):
    model = Order
    empty_value_display = ''
    form_class = OrderForm
    template_name = 'order_create.html'

    def get_initial(self):
        # Pobierz ID klienta przekazane w URL
        client_id = self.kwargs.get('client_id')
        if client_id:
             # Jeśli ID klienta istnieje, pobierz klienta
            client = Client.objects.get(id=client_id)
            # Przypisz klienta do pola klienta formularza jako początkową wartość
            return {'client': client}
        return {}  

    def form_valid(self, form):
            # Pobierz ID klienta przekazane w URL
            client_id = self.kwargs.get('client_id')
            if client_id:
                # Jeśli ID klienta istnieje, pobierz klienta
                client = Client.objects.get(id=client_id)
                # Przypisz klienta do pola klienta formularza jako początkową wartość
                form.instance.client = client
                # Przypisz client_id jako klucz obcy
                form.instance.client_id = client.id
            response = super().form_valid(form)

            # Po zapisaniu obiektu przekieruj użytkownika na stronę z detalami zlecenia
            return redirect('order_detail', client_id=client.id)

class OrderUpdate(LoginRequiredMixin, UpdateView):
    model = Order
    empty_value_display = ''
    form_class = OrderForm
    template_name = 'order_update.html'

    def get_success_url(self):
        return reverse_lazy('order_detail', kwargs={'client_id': self.object.client.pk})
    
    def get_form_kwargs(self):
        kwargs = super(OrderUpdate, self).get_form_kwargs()
        # Przekazujemy obiekt Order jako instance do formularza
        kwargs['instance'] = self.object
        return kwargs

    def form_valid(self, form):
        # Sprawdź czy wybrano status 'wydano', 'rezygnacja' lub 'utylizacja'    
        status = form.cleaned_data.get('status')
        date2 = form.cleaned_data.get('date2')

        if status in ['wydano', 'rezygnacja', 'utylizacja']:
            # Sprawdź czy data2 jest ustawiona
            if not date2:
                messages.error(self.request, 'Proszę uzupełnić datę wydania.')
                return self.form_invalid(form)

            # Sprawdź czy data2 jest większa lub równa date1
            date1 = form.cleaned_data.get('date1')
            if date2 < date1:
                messages.error(self.request, 'Data wydania nie może być wcześniejsza niż data przyjęcia.')
                return self.form_invalid(form)
            
        if date2 is not None and status not in ['wydano', 'rezygnacja', 'utylizacja']:
            messages.error(self.request, 'Jeśli istnieje data wydania, zmień stan realizacji')
            return self.form_invalid(form)

        # Jeśli wszystkie warunki zostały spełnione, zapisz formularz
        return super().form_valid(form)   
    
class JdgUpdate(LoginRequiredMixin, UpdateView):
    model = Jdg
    form_class = JdgForm
    template_name = 'jdg_update.html'
    success_url = reverse_lazy('home')
    jdg_id = 1  # Ustaw stałą identyfikującą obiekt Jdg, który chcesz edytować

    def get_object(self, queryset=None):
        # Zwróć obiekt Jdg o określonym identyfikatorze
        return Jdg.objects.get(pk=self.jdg_id)

    def get_success_url(self) -> str:
        return self.success_url

class OrderDeleteView(LoginRequiredMixin, DeleteView):
    model = Order
    template_name = 'order_confirm_delete.html'
    success_url = reverse_lazy('order_list')

class ClientUpdate(LoginRequiredMixin, UpdateView):
    model = Client
    form_class = ClientForm
    template_name = 'client.html'  # Utwórz odpowiedni szablon HTML dla formularza aktualizacji danych klienta

    def get_success_url(self):
        return reverse_lazy('order_detail', kwargs={'client_id': self.object.pk})
    
    def form_valid(self, form):
        # Ustaw pole is_processed na False przed zapisaniem formularza
        form.instance.is_processed = False
        return super().form_valid(form)    

@login_required(login_url='login')
def import_data_from_json(request, uploaded_file):
    try:
        Client.objects.all().delete()
        Order.objects.all().delete()

        data = json.load(uploaded_file)
        clients = data['data']['clients']
        orders = data['data']['orders']
        jdgs = data['data']['jdgs']

        for jdg_data in jdgs:
            jdg_id = jdg_data['pk']
            jdg_object = get_object_or_404(Jdg, id=jdg_id)  # Pobierz obiekt Jdg na podstawie ID

            # Zaktualizuj pola obiektu Jdg na podstawie danych z pliku JSON
            jdg_object.pole1 = jdg_data['fields']['pole1']
            jdg_object.pole2 = jdg_data['fields']['pole2']
            jdg_object.pole3 = jdg_data['fields']['pole3']
            jdg_object.pole4 = jdg_data['fields']['pole4']
            jdg_object.save()

        with transaction.atomic():
            client_mapping = {}  # Słownik do mapowania starych ID klientów na nowe ID w bazie danych

            # Dodaj klientów do bazy danych i utwórz mapowanie ich starych ID na nowe ID
            for client_data in clients:
                client_id = client_data['pk']  # ID klienta z pliku JSON

                # Sprawdź, czy klient o danym ID już istnieje w słowniku client_mapping
                if client_id not in client_mapping:
                    new_client = Client.objects.create(
                        client=client_data['fields']['client'],
                        phone=client_data['fields']['phone'],
                        uwagi=client_data['fields']['uwagi'],
                        is_processed=client_data['fields']['is_processed']
                    )
                    client_mapping[client_id] = new_client.id  # Dodaj nowe ID klienta do słownika client_mapping

            # Dodaj zamówienia, używając nowych ID klientów
            for order_data in orders:
                date1 = datetime.strptime(order_data['fields']['date1'], '%Y-%m-%d').date()
                date2 = datetime.strptime(order_data['fields']['date2'], '%Y-%m-%d').date() if order_data['fields']['date2'] else None

                status = order_data['fields']['status']
                if status is None and (datetime.now().date() - date1) > timedelta(days=90):
                    status = "wydano"
                if status is None and (datetime.now().date() - date1) < timedelta(days=90):
                    status = "przyjeto"

                client_id = client_mapping.get(order_data['fields']['client'])  # Uzyskaj nowe ID klienta
                if client_id:
                    Order.objects.create(
                        brand=order_data['fields']['brand'],
                        serial=order_data['fields']['serial'],
                        date1=date1,
                        date2=date2,
                        status=status,
                        todo=order_data['fields']['todo'],
                        uwagi=order_data['fields']['uwagi'],
                        naprawa=order_data['fields']['naprawa'],
                        client_id=client_id
                    )

    except Exception as e:
        messages.error(request, f'Wystąpił błąd podczas importowania danych: {e}')
        error_url = reverse_lazy('import_view')
        return redirect(error_url)

@login_required(login_url='login')
def import_view(request):
    if request.method == 'POST':
        form = ImportForm(request.POST, request.FILES)
        if form.is_valid():
            uploaded_file = request.FILES['file']
            import_data_from_json(request, uploaded_file)  # Przekazanie request jako pierwszy argument
            messages.success(request, 'Dane zostały zaimportowane')
            success_url = reverse_lazy('home')
            return redirect(success_url)
    else:
        form = ImportForm()
    return render(request, 'import_template.html', {'form': form})


### WYSZUKIWARKA ###
class OrderSearch(LoginRequiredMixin, ListView):
    model = Order
    template_name = 'order_list.html'
    context_object_name = 'order'
    ordering = ['-id']
    paginate_by = 20
    login_url = '/login/' 

    def get_queryset(self):
        q = self.request.GET.get('q')
        status = self.request.GET.get('status')

        object_list = self.model.objects.all()

        if q:
            object_list = object_list.filter(
                Q(client__client__icontains=q) |
                Q(brand__icontains=q) |
                Q(client__phone__icontains=q) |
                Q(serial__icontains=q) |
                Q(status__icontains=q) |
                Q(todo__icontains=q)
            )

        return object_list.order_by('-id')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        q = self.request.GET.get('q')
        status = self.request.GET.get('status')

        status_title = q if q else "Wszystkie naprawy"

        default_page = 1
        page = self.request.GET.get('page', default_page)
        items = self.get_queryset()
        items_per_page = 20
        paginator = Paginator(items, items_per_page)

        try:
            items_page = paginator.page(page)
        except PageNotAnInteger:
            items_page = paginator.page(default_page)
        except EmptyPage:
            items_page = paginator.page(paginator.num_pages)

        context["items_page"] = items_page
        context["status_title"] = status_title  # Dodaj nowy klucz do kontekstu
        return context
    
### KOPIOWANIE BAZY DO PLIKU###

class CopyOrders(View):
    def get(self, request, *args, **kwargs):
        # Pobierz dane z modeli
        clients = Client.objects.all()
        orders = Order.objects.all()
        jdgs = Jdg.objects.all()
        
        # Serializuj dane do formatu JSON
        clients_json = serialize('json', clients)
        orders_json = serialize('json', orders)
        jdgs_json = serialize('json', jdgs)
        
        # Deserializuj dane JSON do listy słowników
        clients_list = json.loads(clients_json)
        orders_list = json.loads(orders_json)
        jdgs_list = json.loads(jdgs_json)
        
        # Połącz dane w jedną listę słowników
        data_to_save = {
            'clients': clients_list,
            'orders': orders_list,
            'jdgs': jdgs_list
        }
        
        # Zapisz dane do jednego pliku JSON
        with open('backup.json', 'w') as backup_file:
            json.dump(data_to_save, backup_file)
        
        # Zwróć odpowiedź z danymi JSON
        response_data = {
            'message': 'Kopia zapasowa utworzona!',
            'data': data_to_save
        }
        response = HttpResponse(json.dumps(response_data, default=str), content_type='application/json')
        response['Content-Disposition'] = 'attachment; filename=orders.json'

        return response
    
    def post(self, request, *args, **kwargs):
        # Delegate handling of POST requests to the get() method
        return self.get(request, *args, **kwargs)
    
### RODO ###
class CustomerPrivacyView(LoginRequiredMixin, TemplateView):
    template_name = 'customer_privacy.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Oblicz datę sprzed dwóch lat od dzisiaj
        rodo = datetime.now() - timedelta(days=365*2)
        # Znajdź ostatnie naprawy dla każdego klienta, którzy nie są jeszcze przetworzeni
        latest_repairs = Order.objects.values('client').annotate(last_repair=Min('date2')).filter(
            last_repair__lte=rodo, client__is_processed=False
        )
        # Znajdź klientów, dla których ostatnia naprawa miała miejsce ponad 2 lata temu i którzy nie są jeszcze przetworzeni
        clients = Client.objects.filter(id__in=[repair['client'] for repair in latest_repairs]).distinct()
        # Przetwórz dane klientów zgodnie z RODO
        processed_clients = []
        for client in clients:
            # Oblicz skróty dla danych klienta
            client_hash = hashlib.sha256(client.client.encode()).hexdigest()
            processed_client = {
                'id': client.id,
                'client': client_hash[:5],
                'clientold': client.client,
                'phone': client.phone[:5],
                'phoneold': client.phone,
            }
            processed_clients.append(processed_client)
        context['clients'] = processed_clients
        return context
    
class ProcessCustomerDataView(LoginRequiredMixin, View):
    success_url = reverse_lazy('home')

    def post(self, request, *args, **kwargs):
        # Pobierz dane klientów, które mają być przetworzone
        client_ids = request.POST.getlist('client_ids[]')
        # Przetwórz dane klientów zgodnie z RODO
        for client_id in client_ids:
            client = Client.objects.get(id=client_id)
            # Oblicz skróty dla danych klienta
            client_hash = hashlib.sha256(client.client.encode()).hexdigest()[:5]
            phone_hash = hashlib.sha256(client.phone.encode()).hexdigest()[:5]
            client.client = client_hash
            client.phone = phone_hash
            client.is_processed = True
            client.save()

        messages.success(request, 'Dane klientów zostały przetworzone zgodnie z RODO.')
        return redirect(self.success_url)
    

class SingleCustomerPrivacyView(LoginRequiredMixin, TemplateView):
    template_name = 'customer_privacy_single.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        client_id = self.kwargs.get('pk')  # Pobierz ID klienta z parametrów URL
        client = Client.objects.get(id=client_id)  # Pobierz klienta na podstawie ID

        # Oblicz skróty dla danych klienta
        client_hash = hashlib.sha256(client.client.encode()).hexdigest()[:5]
        phone_hash = hashlib.sha256(client.phone.encode()).hexdigest()[:5]

        processed_client = {
            'id': client.id,
            'client': client_hash,
            'clientold': client.client,
            'phone': phone_hash,
            'phoneold': client.phone,
        }

        context['client'] = processed_client
        return context
    
class ProcessSingleCustomerDataView(LoginRequiredMixin, View):
    success_url = reverse_lazy('order_detail', kwargs={'client_id': None})

    def post(self, request, client_id, *args, **kwargs):
        # Przetwórz dane klienta zgodnie z RODO na podstawie przekazanego client_id
        client = get_object_or_404(Client, id=client_id)
        client_hash = hashlib.sha256(client.client.encode()).hexdigest()[:5]
        phone_hash = hashlib.sha256(client.phone.encode()).hexdigest()[:5]
        client.client = client_hash
        client.phone = phone_hash
        client.is_processed = True
        client.save()

        messages.success(request, 'Dane klienta zostały przetworzone zgodnie z RODO.')
        self.success_url = reverse_lazy('order_detail', kwargs={'client_id': client_id})
        return redirect(self.success_url)
