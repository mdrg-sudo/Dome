# Generated by Django 5.1.6 on 2025-02-27 16:39

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Registro',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fechaRegistro', models.DateTimeField(auto_now_add=True)),
                ('valor', models.FloatField(default=0.0)),
                ('cveDispositivo', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='dashboard.dispositivo')),
                ('cveRegistro', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
