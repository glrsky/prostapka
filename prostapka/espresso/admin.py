from django.contrib import admin
from .models import Order, Client

class OrderAdmin(admin.ModelAdmin):
    list_display = ('date1', 'date2', 'brand', 'serial', 'todo', 'naprawa', 'status', 'uwagi', 'client')
    list_filter = ('date1', 'date2')
    search_fields = ('brand', 'serial')

class ClientAdmin(admin.ModelAdmin):
    list_display = ('client', 'phone')
    list_filter = ('client', 'phone')
    search_fields = ('client', 'phone')

admin.site.register(Order, OrderAdmin)
admin.site.register(Client, ClientAdmin)