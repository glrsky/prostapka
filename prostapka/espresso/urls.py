from django.urls import path
from . import views
from .views import ListaNaprawView, OrderUpdate, ClientUpdate, ListaKlientowView, OrderCreate, OrderDeleteView, OrderSearch, CopyOrders, CustomerPrivacyView, ProcessCustomerDataView, ProcessSingleCustomerDataView, SingleCustomerPrivacyView, JdgUpdate

urlpatterns = [
    path("", views.home, name="home"),
    path('import/', views.import_view, name='import_view'),
    path('naprawy/', ListaNaprawView.as_view(), name="order_list"),
    path('naprawy/wrealizacji/', ListaNaprawView.as_view(), {'status': 'w_realizacji'}, name="order_list_A"),
    path('naprawy/utylizacja/', ListaNaprawView.as_view(), {'status': 'utylizacja'}, name="order_list_U"),
    path('naprawy/przyjeto/', ListaNaprawView.as_view(), {'status': 'przyjeto'}, name="order_list_P"),
    path('naprawy/dowydania/', ListaNaprawView.as_view(), {'status': 'do wydania'}, name="order_list_W"),
    path('naprawy/rezygnacja/', ListaNaprawView.as_view(), {'status': 'rezygnacja z naprawy'}, name="oder_list_R"),
    path('kartaklienta/<int:client_id>/', views.detail_order, name="order_detail"),
    path('kartaklienta/aktualizuj/<int:pk>/', OrderUpdate.as_view(), name='order_update'),
    path('client/<int:pk>/update/', ClientUpdate.as_view(), name='client_update'),
    path('klienci/', ListaKlientowView.as_view(), name='client_list'),
    path('nowe-zamowienie/', views.create_or_get_client, name='create_or_get_client'),
    path('nowe-zamowienie/<int:client_id>/', OrderCreate.as_view(), name='order_create'),
    path('nowy-klient/', views.create_client, name='create_client'),
    path('order/<int:pk>/delete/', OrderDeleteView.as_view(), name='order_delete'),
    path('client/<int:pk>/delete/', views.ClientDeleteView.as_view(), name='client_delete'),
    path('wyszukiwarka/', OrderSearch.as_view(), name="order_search"),
    path('kopia/', CopyOrders.as_view(), name='copy_orders'),
    path('customer_privacy/', CustomerPrivacyView.as_view(), name='customer_privacy'),
    path('process_customer_data/', ProcessCustomerDataView.as_view(), name='process_customer_data'),
    path('process_single_customer_data/<int:client_id>/', ProcessSingleCustomerDataView.as_view(), name='process_single_customer_data'),
    path('single_customer_privacy/<int:pk>/', SingleCustomerPrivacyView.as_view(), name='single_customer_privacy'),
    path('confirm/<int:pk>/', views.confirm, name="confirm"),
    path('jdg/update/', JdgUpdate.as_view(), name='jdg_update'),
    path('login/', views.login_user, name='login'),
    path('logout/', views.logout_user, name="logout"),
]