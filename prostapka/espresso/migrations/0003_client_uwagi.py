# Generated by Django 4.2.6 on 2023-10-07 16:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('espresso', '0002_alter_client_phone'),
    ]

    operations = [
        migrations.AddField(
            model_name='client',
            name='uwagi',
            field=models.CharField(blank=True, max_length=120, null=True),
        ),
    ]
