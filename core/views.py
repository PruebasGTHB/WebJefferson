from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth import logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test


# Verifica si el usuario es administrador
def es_admin(user):
    return user.is_superuser


# Vista de login
def login_view(request):
    if request.user.is_authenticated:
        return redirect('home_redirect')

    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('home_redirect')
        else:
            messages.error(request, 'Usuario o contraseña incorrectos')

    return render(request, 'registration/login.html')


# Redirecciona al ingreso correcto según tipo de usuario
@login_required
def home_redirect(request):
    if request.user.is_superuser:
        return redirect('ingresos_admin')
    else:
        return redirect('ingresos_usuario')


# Vista común para todos: el banner o layout general
@login_required
def inicio_usuario(request):
    return render(request, 'core/index_usuario.html')


# VISTAS USUARIO
@login_required
def ingresos_usuario(request):
    return render(request, 'core/ingresos_usuario.html')


@login_required
def constantes_usuario(request):
    return render(request, 'core/constantes_usuario.html')


@login_required
def indicadores_usuario(request):
    return render(request, 'core/indicadores_usuario.html')


@login_required
def dashboards_usuario(request):
    return render(request, 'core/dashboards_usuario.html')


# VISTAS ADMINISTRADOR
@login_required
@user_passes_test(es_admin, login_url='ingresos_usuario')
def ingresos_admin(request):
    return render(request, 'core/ingresos_admin.html')


@login_required
@user_passes_test(es_admin, login_url='ingresos_usuario')
def constantes_admin(request):
    return render(request, 'core/constantes_admin.html')


@login_required
@user_passes_test(es_admin, login_url='ingresos_usuario')
def indicadores_admin(request):
    return render(request, 'core/indicadores_admin.html')


@login_required
@user_passes_test(es_admin, login_url='ingresos_usuario')
def dashboards_admin(request):
    return render(request, 'core/dashboards_admin.html')
