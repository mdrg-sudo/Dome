from django.db import models
from django.contrib.auth.models import User

# Tabla de registro
class Registro(models.Model):
    cveDispositivo = models.ForeignKey('Dispositivo', on_delete=models.CASCADE)
    cveRegistro = models.ForeignKey(User, on_delete=models.CASCADE)
    fechaRegistro = models.DateTimeField(auto_now_add=True)
    valor = models.FloatField(default=0.0)

    def __str__(self):
        return f"Registro {self.id} - Dispositivo: {self.cveDispositivo.nombre}, Usuario: {self.cveRegistro.username}"

# Tabla dispositivo
class Dispositivo(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True)
    estatus = models.BooleanField(default=True)
    fechaRegistro = models.DateTimeField(auto_now_add=True)
    

    def __str__(self):
        return self.nombre
