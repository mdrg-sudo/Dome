from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.contrib.auth import login, logout, authenticate
from .models import Dispositivo, Registro
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Sum, Avg
from django.db.models.functions import TruncDate
from django.views.decorators.csrf import csrf_exempt
import json
import logging

logger = logging.getLogger(__name__)

# Rangos de temperatura para análisis
TEMP_BAJA = 15
TEMP_OPTIMA_BAJA = 20
TEMP_OPTIMA_ALTA = 25
TEMP_ALTA_BAJA = 28
TEMP_MUY_ALTA = 30

def analizar_riego(temperatura):
    mensaje_descriptivo = ""
    mensaje_predictivo = ""
    alerta_riego = "Normal"

    if temperatura < TEMP_BAJA:
        mensaje_descriptivo = "La temperatura actual es muy baja. El riesgo de necesidad de riego es mínimo."
        mensaje_predictivo = "Se espera una baja necesidad de riego en condiciones frías."
        alerta_riego = "Baja"
    elif TEMP_BAJA <= temperatura < TEMP_OPTIMA_BAJA:
        mensaje_descriptivo = "La temperatura actual es baja. El riesgo de necesidad de riego es bajo."
        mensaje_predictivo = "Se espera una necesidad de riego baja a moderada si las condiciones persisten."
        alerta_riego = "Baja"
    elif TEMP_OPTIMA_BAJA <= temperatura < TEMP_OPTIMA_ALTA:
        mensaje_descriptivo = "La temperatura actual es óptima. La necesidad de riego es normal."
        mensaje_predictivo = "Se espera una necesidad de riego normal para un crecimiento saludable."
        alerta_riego = "Normal"
    elif TEMP_OPTIMA_ALTA <= temperatura < TEMP_ALTA_BAJA:
        mensaje_descriptivo = "La temperatura actual es alta. El riesgo de necesidad de riego es elevado."
        mensaje_predictivo = "Se prevé una mayor necesidad de riego para evitar el estrés hídrico."
        alerta_riego = "Alta"
    elif TEMP_ALTA_BAJA <= temperatura < TEMP_MUY_ALTA:
        mensaje_descriptivo = "La temperatura actual es muy alta. La necesidad de riego es alta."
        mensaje_predictivo = "Se requiere riego pronto para prevenir daños por calor y sequedad."
        alerta_riego = "Alta"
    else:
        mensaje_descriptivo = "La temperatura actual es extremadamente alta. ¡Riego urgente necesario!"
        mensaje_predictivo = "Se espera una necesidad de riego crítica para la supervivencia de las plantas."
        alerta_riego = "Urgente"

    return {"descriptivo": mensaje_descriptivo, "predictivo": mensaje_predictivo, "alerta": alerta_riego}


def helloworld(request):
    return render(request, 'home.html', {'form': ''})


def iniciarSesion(request):
    if request.method == 'GET':
        return render(request, 'login.html', {'form': AuthenticationForm})
    else:
        user = authenticate(request, username=request.POST['username'], password=request.POST['password'])
        if user is None:
            return render(request, 'login.html', {'form': AuthenticationForm,
                           'error': 'El usuario o contraseña son incorrectos'})
        else:
            login(request, user)
            logger.info(f"Usuario {user.username} ha iniciado sesión.")
            return redirect('/')


def cerrarSesion(request):
    logger.info(f"Usuario {request.user.username} cerró sesión.")
    logout(request)
    return redirect('/')


def registro(request):
    if request.method == 'GET':
        return render(request, 'registro.html', {'form': UserCreationForm})
    else:
        if request.POST['password1'] == request.POST['password2']:
            try:
                user = User.objects.create_user(username=request.POST['username'], password=request.POST['password1'])
                user.save()
                login(request, user)
                logger.info(f"Nuevo usuario registrado: {user.username}")
                return redirect('/')
            except IntegrityError:
                return render(request, 'registro.html',
                              {'form': UserCreationForm, 'error': 'El usuario ya existe'})
        return render(request, 'registro.html', {'form': UserCreationForm, 'error': 'Las contraseñas no coinciden'})


@login_required
def dispositivos(request):
    dispositivos = Dispositivo.objects.all()
    return render(request, 'dispositivos.html', {'dispositivos': dispositivos})


def dashboard(request):
    datos = Registro.objects.annotate(
        fecha=TruncDate('fechaRegistro')
    ).values('fecha').annotate(
        valor_promedio=Avg('valor')
    ).order_by('fecha')

    promedio_obj = Registro.objects.aggregate(promedio=Avg('valor'))
    promedio_temperatura = promedio_obj['promedio'] if promedio_obj['promedio'] is not None else 0

    ultimo_registro = Registro.objects.order_by('-fechaRegistro').first()
    temperatura_actual = ultimo_registro.valor if ultimo_registro else 0

    analisis = analizar_riego(temperatura_actual)

    context = {
        'datos': datos,
        'promedio': {'total': promedio_temperatura},
        'temperatura_actual': temperatura_actual,
        'mensaje_descriptivo': analisis['descriptivo'],
        'mensaje_predictivo': analisis['predictivo'],
        'alerta_riego': analisis['alerta']
    }
    return render(request, 'dashboard.html', context)


def datos_tiempo_real(request):
    return render(request, 'tiempo.html')


@csrf_exempt
def agregar_dispositivo(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            logger.info(f"Datos recibidos para agregar dispositivo: {data}")
            nombre = data.get('nombre')
            descripcion = data.get('descripcion')
            estatus = data.get('estatus')

            if not all([nombre, descripcion, estatus]):
                return JsonResponse({'mensaje': 'Faltan campos obligatorios'}, status=400)

            dispositivo = Dispositivo.objects.create(
                nombre=nombre, descripcion=descripcion, estatus=estatus)
            return JsonResponse({'mensaje': 'Dispositivo agregado correctamente', 'id': dispositivo.id})
        except Exception as e:
            logger.error(f"Error al agregar dispositivo: {e}")
            return JsonResponse({'mensaje': f'Error: {e}'}, status=400)
    return JsonResponse({'mensaje': 'Método no permitido'}, status=405)


@csrf_exempt
def agregar_registro(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            logger.info(f"Datos recibidos para agregar registro: {data}")
            dispositivo_id = data.get('dispositivo_id')
            usuario_id = data.get('usuario_id')
            valor = data.get('valor')

            if not all([dispositivo_id, usuario_id, valor]):
                return JsonResponse({'mensaje': 'Faltan campos obligatorios'}, status=400)

            dispositivo = Dispositivo.objects.get(id=dispositivo_id)
            usuario = User.objects.get(id=usuario_id)

            registro = Registro.objects.create(
                cveDispositivo=dispositivo, cveRegistro=usuario, valor=valor)
            return JsonResponse({'mensaje': 'Registro agregado correctamente', 'id': registro.id})
        except Exception as e:
            logger.error(f"Error al agregar registro: {e}")
            return JsonResponse({'mensaje': f'Error: {e}'}, status=400)
    return JsonResponse({'mensaje': 'Método no permitido'}, status=405)


@csrf_exempt
def editar_dispositivo(request, dispositivo_id):
    logger.info(f"Editar dispositivo {dispositivo_id} solicitado")
    dispositivo = get_object_or_404(Dispositivo, id=dispositivo_id)
    if request.method == 'PUT':
        try:
            data = json.loads(request.body)
            logger.info(f"Datos recibidos para editar: {data}")
            dispositivo.nombre = data.get('nombre')
            dispositivo.descripcion = data.get('descripcion')
            dispositivo.estatus = data.get('estatus')
            dispositivo.save()
            return JsonResponse({'mensaje': 'Dispositivo actualizado correctamente'})
        except Exception as e:
            logger.error(f"Error al editar dispositivo {dispositivo_id}: {e}")
            return JsonResponse({'mensaje': f'Error: {e}'}, status=400)
    return JsonResponse({'mensaje': 'Método no permitido'}, status=405)


@csrf_exempt
def eliminar_dispositivo(request, dispositivo_id):
    logger.info(f"Eliminar dispositivo {dispositivo_id} solicitado")
    dispositivo = get_object_or_404(Dispositivo, id=dispositivo_id)
    if request.method == 'DELETE':
        try:
            dispositivo.delete()
            return JsonResponse({'mensaje': 'Dispositivo eliminado correctamente'})
        except Exception as e:
            logger.error(f"Error al eliminar dispositivo {dispositivo_id}: {e}")
            return JsonResponse({'mensaje': f'Error: {e}'}, status=400)
    return JsonResponse({'mensaje': 'Método no permitido'}, status=405)


@login_required
def lista_registros(request):
    user = request.user
    logger.info(f"Usuario {user.username} consultó sus registros")
    registros = Registro.objects.filter(cveRegistro=user.id).order_by('fechaRegistro')
    return render(request, 'control.html', {'registros': registros})

       