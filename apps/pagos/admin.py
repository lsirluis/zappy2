from django.contrib import admin

# Register your models here.
from apps.pagos.models import Recibo, Detalle, RecibosPagos,RecibosyComprobante,\
							RecibosAuto,Abono,Interes,Noticia,DeNoticia
							# CuotaExtraordinaria

admin.site.register(Recibo)
admin.site.register(Detalle)
admin.site.register(RecibosPagos)
admin.site.register(RecibosyComprobante)
admin.site.register(RecibosAuto)
admin.site.register(Abono)
admin.site.register(Interes)
admin.site.register(Noticia)
admin.site.register(DeNoticia)
# admin.site.register(CuotaExtraordinaria)
