from django.contrib import admin

# Register your models here.
from apps.pagos.models import Recibo, Detalle

admin.site.register(Recibo)
admin.site.register(Detalle)

