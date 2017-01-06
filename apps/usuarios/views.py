from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from apps.usuarios.models import Administrador

# Create your views here.
def index(request):
	return HttpResponse("Hola esta es la pagina para usuarios")
# @login_required()
def listar(request):
	usuarios = Administrador.objects.all()
	contexto = {'usuario': usuarios}
	return render(request, 'Usuarios/Usuarios_list.html',contexto)