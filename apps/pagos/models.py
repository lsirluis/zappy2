from django.db import models
from apps.edificios.models import Unidad, Propiedad
from apps.usuarios.models import Administrador

# Create your models here.

class Recibo(models.Model):

	id = models.AutoField(primary_key=True)
	unidad = models.ForeignKey(Unidad, on_delete=models.CASCADE)
	estado = models.PositiveIntegerField(null=False, blank=False)
	descripcion = models.CharField(max_length = 120, null=True, blank=True)
	numConsecutivo= models.IntegerField()
	fecha_generacion = models.DateTimeField(auto_now_add=True)
	fecha_cobrada = models.DateField()
	fecha_vencimiento= models.DateField()
	fecha_actualizacion= models.DateTimeField(auto_now=True)
	class Meta:
		verbose_name='Recibo'
		verbose_name_plural='Recibos'
	def __str__(self): #forma 2
		return '{}-{}'.format(self.unidad,self.fecha_cobrada)	

class RecibosPagos(models.Model):
	id = models.AutoField(primary_key=True)
	unidad = models.ForeignKey(Unidad, on_delete=models.CASCADE)
	fecha_generacion = models.DateTimeField(auto_now_add=True)
	fecha_actualizacion= models.DateTimeField(auto_now=True)
	no_comprobante = models.PositiveIntegerField(null=False, blank=False)
	pagador = models.CharField(max_length=100,verbose_name='RecibioDe')
	suma = models.BigIntegerField(null=False, blank=False)
	enletras= models.CharField(max_length = 200, null=False, blank=False )
	concepto= models.CharField(max_length = 200, null=False, blank=False )
	FORMAPAGO_choose = ((0,'Cheque'),(1,'Banco'),(2,'Efectivo'),(3,'Transferencia'))
	forma_pago= models.PositiveIntegerField(choices = FORMAPAGO_choose, default=2)
	referencia1 = models.CharField(max_length=50,null=True, blank=True )
	referencia2 = models.CharField(max_length=50, null=True, blank=True)
	recibo = models.ForeignKey(Recibo, on_delete = models.CASCADE,null=False, blank=False)
	TIPOPAGO_choose = ((0,'PagoTotal'),(1,'Abono'))
	tipo = models.PositiveIntegerField(choices = TIPOPAGO_choose, default=2)
	class Meta:
		verbose_name='Recibo Pago'
		verbose_name_plural='Recibos Pagos'
	def __str__(self): #forma 2
		return '{}-{}'.format(self.unidad,self.suma)

class RecibosyComprobante(models.Model):
	id = models.AutoField(primary_key=True)
	recibo = models.ForeignKey(Recibo, on_delete = models.CASCADE)
	comprobante = models.ForeignKey(RecibosPagos ,  on_delete = models.CASCADE)
	TIPOPAGO_choose = ((0,'Pago'),(1,'Abono'))
	tipo = models.PositiveIntegerField(choices = TIPOPAGO_choose, default=0)

	

class RecibosAuto(models.Model):
	id =models.AutoField(primary_key=True)
	idRecibo = models.ForeignKey(Recibo, on_delete=models.CASCADE)
	

class Detalle(models.Model):
	id = models.AutoField(primary_key=True)
	idRecibo = models.ForeignKey(Recibo, on_delete= models.CASCADE)
	valor = models.BigIntegerField(blank=False, null=False)
	tipo = models.CharField(max_length= 100)
	descripcion = models.CharField(max_length = 120)
	fecha_generacion=models.DateTimeField(auto_now_add=True)
	fecha_actualizacion=models.DateTimeField(auto_now=True)
	class Meta:
		verbose_name='Detalle'
		verbose_name_plural='Detalles'
	def __str__(self): #forma 2
		return '{}-{}'.format(self.tipo,self.valor)	

class Abono(models.Model):
	id = models.AutoField(primary_key=True)
	detalle = models.ForeignKey(Detalle, on_delete = models.CASCADE)
	valor_inicial = models.PositiveIntegerField()
	valor_abonado = models.PositiveIntegerField()
	valor_restante = models.PositiveIntegerField()

class Deuda(models.Model):
	id = models.AutoField(primary_key=True)
	idDetalle = models.ForeignKey(Detalle, on_delete= models.CASCADE)
	tipo = models.CharField(max_length= 100)
	IdReciboDeuda = models.ForeignKey(Recibo, on_delete= models.CASCADE)
	fecha_generacion=models.DateTimeField(auto_now_add=True)
	fecha_actualizacion=models.DateTimeField(auto_now=True)
	unidad = models.ForeignKey(Unidad, on_delete= models.CASCADE, blank=False, null=False)
	class Meta:
		verbose_name='Deuda'
		verbose_name_plural='Deudas'
	def __str__(self): #forma 2
		return '{}-{}'.format(self.tipo,self.IdReciboDeuda)	


class Interes(models.Model):
	id = models.AutoField(primary_key=True)
	idRecibo = models.ForeignKey(Recibo, on_delete= models.CASCADE)
	interesAplicado = models.PositiveIntegerField()
	valorinteres = models.BigIntegerField(blank=False, null=False)
	fecha_generacion = models.DateTimeField(auto_now_add=True)
	fecha_actualizacion = models.DateTimeField(auto_now=True)

class Noticia(models.Model):
	#el estado indica si fue vista(1),si no(0) y 2 si pasaron 7 dias sin verlo.
	# el estado pasara a 2 cuando pasen 7 dias,sin ser visto
	# el estado pasara a visto cuando administrador presione sobre el boton visto
	# la descripcion es para saber si se genero automaticamente
	id = models.AutoField(primary_key=True)
	administrador = models.ForeignKey(Administrador, on_delete=models.CASCADE)
	ESTADONOTICIA_choose = ((0,'No visto'),(1,'Visto'),(3,'No visto 7 Dias'))
	estado = models.PositiveIntegerField(choices=ESTADONOTICIA_choose,default = 0, null=False, blank=False)
	descripcion = models.CharField(max_length = 120, null=True, blank=True)
	fecha_generacion = models.DateTimeField(auto_now_add=True)
	propiedad= models.ForeignKey(Propiedad, on_delete=models.CASCADE)
	class Meta:
		verbose_name='Noticia'
		verbose_name_plural='Noticias'
	def __str__(self): #forma 2
		return '{}-{}'.format(self.propiedad,self.estado)	

class DeNoticia(models.Model):
	id = models.AutoField(primary_key=True)
	idNoticia = models.ForeignKey(Noticia, on_delete= models.CASCADE)
	unidad = models.ForeignKey(Unidad, on_delete=models.CASCADE)
	idRecibo = models.ForeignKey(Recibo, on_delete= models.CASCADE)
	class Meta:
		verbose_name='Detalle noticia'
		verbose_name_plural='Detalles noticias'
	def __str__(self): #forma 2
		return '{}{}'.format(self.idNoticia,self.unidad)	
