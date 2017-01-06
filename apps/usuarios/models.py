from django.db import models
from django.contrib.auth.models import User


# Create your models here.
# class Administrador(models.Model):
# 	identificacion=models.CharField(max_length=50, primary_key=True)
# 	nombre = models.CharField( max_length=50)
# 	apellido = models.CharField(max_length=20, )
# 	# user = models.CharField(max_length=20)
# 	# password = models

# 	def __str__(self): #forma 2
# 		return '{} {}'.format(self.nombre, self.apellido)

class Departamento(models.Model):
	id = models.AutoField(primary_key=True)
	nombre = models.CharField(max_length = 30, blank=False)
	Cod_departamento = models.IntegerField()
	class Meta:
		verbose_name='Departamento'
		verbose_name_plural= 'Departamentos'
	def __str__(self): #forma 2
		return '{}'.format(self.nombre)	

class Ciudad(models.Model):
	id = models.AutoField(primary_key=True)
	nombre = models.CharField(max_length = 30, blank=False)
	Cod_ciudad = models.IntegerField()
	Cod_departamento = models.ForeignKey(Departamento, on_delete=models.CASCADE, blank=False)
	class Meta:
		verbose_name='Ciudad'
		verbose_name_plural='Ciudades'
	def __str__(self): #forma 2
		return '({}) {}'.format(self.Cod_departamento.nombre, self.nombre)



class Administrador(models.Model):
	idu = models.OneToOneField(User, on_delete=models.CASCADE, blank=False, primary_key=True)
	TIPOIDENTIDICACION_choose= ((1,'cedula'),(2,'Tarjeta identidad'),(3,'Pasaporte'),(4,'Contraseña'))
	tipoidentidicacion = models.IntegerField(choices = TIPOIDENTIDICACION_choose, default=1)
	identificacion = models.CharField(max_length = 50 , blank=False, unique=True)
	nombre1 = models.CharField(max_length=50, blank=False)
	nombre2 = models.CharField(max_length=50)
	apellido1 = models.CharField(max_length=50, blank=False)
	apellido2 = models.CharField(max_length=50)
	tel = models.IntegerField()
	cel = models.BigIntegerField()
	direccion = models.CharField(max_length = 120)
	email = models.EmailField(max_length = 120 , blank=False, unique=True)
	ciudad = models.ForeignKey(Ciudad, on_delete=models.CASCADE, blank=False)
	class Meta:
		verbose_name='Administrador'
		verbose_name_plural='Administradores'

	def __str__(self): #forma 
		return '({})-{} {}'.format(self.identificacion, self.nombre1, self.apellido1)	


