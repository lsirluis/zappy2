from django.contrib import admin

# Register your models here.
from apps.edificios.models import Propiedad, Unidad , Persona, Banco
# Register your models here.

# admin.site.register(Propiedad)	
admin.site.register(Propiedad,list_display = ('ciudad','nombre', 'direccion','administrador','tipo','presupuesto_anual'))
admin.site.register(Unidad,list_display = ('propiedad','torre','numero', 'residente','propietario','responsable'))
admin.site.register(Persona)
admin.site.register(Banco, list_display=('banco','tipo_cuenta','num_cuenta', 'propiedad'))

