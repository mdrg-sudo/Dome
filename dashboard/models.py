from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.models import User  # Si deseas usar el modelo de usuario predeterminado de Django


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
    
#Tabla usuarios

class Usuario(models.Model):
    nombre = models.CharField(max_length=25)
    apellido = models.CharField(max_length=25)
    rol = models.CharField(max_length=25)
    usuario = models.CharField(max_length=30, unique=True)
    contrasenia = models.CharField(max_length=60)

    def __str__(self):
        return f"{self.nombre} {self.apellido} ({self.usuario})"


#Tabla Cultivo
class Cultivo(models.Model):
    nombre = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.nombre
    
#Tabla invernadero

class Invernadero(models.Model):
    cultivo = models.ForeignKey(Cultivo, on_delete=models.CASCADE, related_name='invernaderos')
    detalles = models.CharField(max_length=70)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='invernaderos')

    def __str__(self):
        return f"Invernadero de {self.cultivo.nombre} - {self.detalles}"

#Tabla sensores

class Sensor(models.Model):
    TIPO_SENSOR_CHOICES = [
        ('Temperatura', 'Temperatura'),
        ('Humedad', 'Humedad'),
        ('Luz', 'Luz'),
        ('Sueldo', 'Sueldo'),
        # Puedes agregar más tipos de sensores según lo necesites
    ]
    
    tipo = models.CharField(max_length=50, choices=TIPO_SENSOR_CHOICES)
    descripcion = models.TextField()
    fecha_instalacion = models.DateTimeField(auto_now_add=True)
    invernadero = models.ForeignKey('Invernadero', on_delete=models.CASCADE, related_name='sensores')

    def __str__(self):
        return f"Sensor de {self.tipo} en {self.invernadero.detalles}"
    
#Tabla datos sensores
class Datos_Sensores(models.Model):
    valor = models.DecimalField(max_digits=10, decimal_places=2)  # Campo para almacenar el valor medido
    fecha = models.DateTimeField(auto_now_add=True)  # Fecha en la que se registró el dato
    sensor = models.ForeignKey(Sensor, on_delete=models.CASCADE, related_name='datos')

    def __str__(self):
        return f"Valor: {self.valor} para el Sensor: {self.sensor.tipo} - {self.fecha}"