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
