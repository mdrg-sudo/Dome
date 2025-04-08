from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.contrib.auth import login, logout, authenticate
from .models import Dispositivo, Registro
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Sum
from django.views.decorators.csrf import csrf_exempt
import json
import logging

logger = logging.getLogger(__name__)

##Prueba commit 

def helloworld(request):
    return render(request, 'home.html', {'form': ''})

def iniciarSesion(request):
    if request.method == 'GET':
        return render(request, 'login.html', {'form': AuthenticationForm})
    else:
        user = authenticate(request, username=request.POST['username'], password=request.POST['password'])
        if user is None:
            return render(request, 'login.html', {'form': AuthenticationForm, 'error': 'El usuario o contraseña son incorrectos'})
        else:
            login(request, user)
            return redirect('/')

def cerrarSesion(request):
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
                return redirect('/')
            except IntegrityError:
                return render(request, 'registro.html', {'form': UserCreationForm, 'error': 'El usuario ya existe'})
        return render(request, 'registro.html', {'form': UserCreationForm, 'error': 'Las contraseñas no coinciden'})

@login_required
def dispositivos(request):
    dispositivos = Dispositivo.objects.all()
    return render(request, 'dispositivos.html', {'dispositivos': dispositivos})

def dashboard(request):

    datos = Registro.objects.values('fechaRegistro').annotate(valor_promedio=(Sum('valor') / Count('valor'))).order_by()

    promedio = Registro.objects.aggregate(total=(Sum('valor') / Count('valor')))
    return render(request, 'dashboard.html', {
        'datos' : datos,
        'promedio' : promedio
    
    })

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

            dispositivo = Dispositivo.objects.create(nombre=nombre, descripcion=descripcion, estatus=estatus)
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

            dispositivo = Dispositivo.objects.get(id=dispositivo_id)
            usuario = User.objects.get(id=usuario_id)

            registro = Registro.objects.create(cveDispositivo=dispositivo, cveRegistro=usuario, valor=valor)
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
    print(user.id)
    registros = Registro.objects.filter(cveRegistro=user.id).order_by('fechaRegistro')
    return render(request, 'control.html', {'registros': registros})

       