from django.contrib import admin

# Register your models here.
from apps.usuarios.models import Administrador, Departamento, Ciudad
# Register your models here.

admin.site.register(Administrador,list_display = ('identificacion','nombre1', 'apellido1'))
admin.site.register(Ciudad)
admin.site.register(Departamento)
