# Generated by Django 4.2.6 on 2023-10-12 12:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('espresso', '0005_alter_client_client_alter_client_phone'),
    ]

    operations = [
        migrations.CreateModel(
            name='Jdg',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('pole1', models.CharField(default='Informuję, że Pana/Pani dane będą przetwarzane zgodnie z Ogólnym Rozporządzeniem w zakresie danych osobowych z dnia 27 kwietnia 2016 r.', max_length=150)),
                ('pole2', models.CharField(default='Administratorem tych danych jest DANE FIRMY. Szczegółowe informacje odnośnie danych osobowych znajdują się na stronie ADRES', max_length=150)),
                ('pole3', models.CharField(default='dodatkowe info', max_length=150)),
                ('pole4', models.CharField(default='kontakt z serwisem: tel. XXXX tel. XXX', max_length=150)),
            ],
        ),
    ]