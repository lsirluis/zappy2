from django.db import models
from apps.usuarios.models import Administrador, Ciudad
# Create your models here.
# class Propiedad(models.Model):
# 	identificacion=models.CharField(max_length=50, primary_key=True)
# 	nombre = models.CharField( max_length=50)
# 	direccion = models.TextField()
# 	administrador = models.ForeignKey(Administrador,verbose_name='administradors')
# 	class Meta:
# 		verbose_name='Tipo de conjunto'
# 		verbose_name_plural='Tipos de conjuntos'
# 	# def __str__(self): #forma 1 
# 	# 	return '%s %s' % (self.nombre, self.apellidos)
# 	def __str__(self): #forma 2
# 		return '{}'.format(self.nombre)

# class Unidad(models.Model):
# 	propiedad = models.ForeignKey(Propiedad)
# 	torre = models.CharField(max_length=5)
# 	numero = models.IntegerField()
# 	def __str__(self): #forma 2
# 		return '{}'.format(self.numero)

class Propiedad(models.Model):
	idlegal = models.CharField(max_length = 50, unique = True, blank = False, primary_key=True, verbose_name='Identidad')
	nombre = models.CharField(max_length = 50, blank = False)
	direccion = models.CharField(max_length = 50,blank = False)
	telefono = models.IntegerField()
	ciudad = models.ForeignKey(Ciudad, on_delete = models.CASCADE, blank = False)
	administrador = models.ForeignKey(Administrador, on_delete = models.CASCADE, blank = False)
	area = models.IntegerField()
	TIPOPROPIEDAD_choose = ((1,'Residencial'),(2,'Comercial'),(3,'Mixto'))
	tipo = models.IntegerField(choices = TIPOPROPIEDAD_choose, default = 1, verbose_name='Tipo Propiedad')
	fecha_registro = models.DateTimeField(auto_now=False, auto_now_add=True, blank=True, null=True)	
	presupuesto_anual = models.IntegerField()
	dia_cobro = models.IntegerField()
	porcentaje_mora = models.FloatField()
	Imagen = models.ImageField(upload_to = 'Img/Propiedad/', blank=True, default = 'Img/Propiedad/default_building_zappy.jpg')

	class Meta:
		verbose_name='Propiedad'
		verbose_name_plural='Propiedades'
	def __str__(self): #forma 2
		return '({}) {}'.format(self.idlegal, self.nombre)

class Persona(models.Model):
	id = models.AutoField(primary_key=True)
	identificacion = models.CharField(max_length = 30, blank=True, null=True)
	nombre = models.CharField(max_length = 30)
	apellido = models.CharField(max_length = 30)
	email = models.EmailField(max_length=250, blank=False, unique=True)
	celular = models.BigIntegerField(blank=True, null=True)
	telefono = models.PositiveIntegerField(verbose_name='Telefono', blank=False, null=False)
	administrador = models.ForeignKey(Administrador, on_delete = models.CASCADE,blank=False, null=False)
	TIPO_choose = ((1,'Natural'),(2,'Juridica'))
	tipo = models.IntegerField(choices = TIPO_choose, default = 1)
	propiedad = models.ForeignKey(Propiedad,on_delete=models.CASCADE)


	class Meta:
		verbose_name='Persona'
		verbose_name_plural='Personas'

	def __str__(self): #forma 2
		return '({}) {} {}'.format(self.identificacion, self.nombre,self.apellido)	

class Unidad(models.Model):
	id = models.AutoField(primary_key=True)
	propiedad = models.ForeignKey(Propiedad, on_delete = models.CASCADE)
	torre = models.CharField(max_length=5)
	numero = models.PositiveIntegerField()
	ESTADOAPTO = ((1,'Habitado'),(2,'Deshabitado'),(3,'En construccion'))
	estado = models.IntegerField(choices = ESTADOAPTO, default= 1)
	dia_cobro = models.PositiveIntegerField(default=1)
	residente = models.ForeignKey(Persona, on_delete = models.CASCADE, related_name='Unidad_residente', null=True, blank=True)
	propietario = models.ForeignKey(Persona, on_delete = models.CASCADE, related_name='Unidad_propietario')
	arrendatario = models.ForeignKey(Persona, on_delete = models.CASCADE, related_name='Unidad_arrendatario',null=True, blank=True)
	RESPONSABLE_choose = ((1,'Residente'),(2,'Propietario'),(3,'Arrendatario'))
	responsable = models.IntegerField(choices=RESPONSABLE_choose , default = 2)
	fecha_registro = models.DateTimeField(auto_now=False, auto_now_add=True)
	FORMARECIBO_choose = ((1,'Fisico'),(2,'Email'))
	forma_recibo = models.IntegerField(choices=FORMARECIBO_choose, default = 1)
	saldo_favor = models.PositiveIntegerField(null= True,blank=True,default=0)
	porcentaje_mora = models.FloatField(default=0.0)
	valor_mora = models.PositiveIntegerField(null = True,blank=True,default=0)
	coeficiente = models.FloatField(default=1.0, )
	valor_pago = models.PositiveIntegerField(blank=False, null=False, default=0) 
	TIPOUnidad_choose = ((1,'Residencial'),(2,'Comercial'))
	tipo = models.IntegerField(choices = TIPOUnidad_choose, default=1)
	class Meta:
		verbose_name='Unidad'
		verbose_name_plural='Unidades'
	def __str__(self): #forma 2
		return '{}-{}'.format(self.torre,self.numero)	

class Banco(models.Model):
	id = models.AutoField(primary_key=True)
	administrador = models.ForeignKey(Administrador, on_delete = models.CASCADE, blank = False)
	TIPOCUENTA_choose=((1,'Corriente'),(2,'Ahorro'))
	banco = models.CharField(max_length=254,verbose_name='Banco')
	tipo_cuenta = models.IntegerField(choices = TIPOCUENTA_choose, default = 2,verbose_name='Tipo de Cuenta')
	num_cuenta = models.CharField(max_length=245, null=False, blank=False, verbose_name='# Cuenta')
	propiedad = models.ForeignKey(Propiedad, on_delete=models.CASCADE, blank=False, null=False)
	class Meta:
		verbose_name='Banco'
		verbose_name_plural="Bancos"
	def __str__(self):
		return '{} {}'.format(self.Banco,self.num_cuenta)
