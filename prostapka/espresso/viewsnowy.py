
@login_required(login_url='login')
def import_data_from_json(request, uploaded_file):
    try:
        Client.objects.all().delete()
        Order.objects.all().delete()

        data = json.load(uploaded_file)
        clients = data['data']['clients']
        orders = data['data']['orders']
        jdgs = data['data']['jdgs']

        with transaction.atomic():
            for jdg_data in jdgs:
                jdg_id = jdg_data['id']
                jdg_object = get_object_or_404(Jdg, id=jdg_id)  # Pobierz obiekt Jdg na podstawie ID

                # Zaktualizuj pola obiektu Jdg na podstawie danych z pliku JSON
                jdg_object.pole1 = jdg_data['fields']['pole1']
                jdg_object.pole2 = jdg_data['fields']['pole2']
                jdg_object.pole3 = jdg_data['fields']['pole3']
                jdg_object.pole4 = jdg_data['fields']['pole4']
                jdg_object.save()

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