from django import forms

from apps.edificios.models import Propiedad, Persona, Unidad, Banco
from apps.usuarios.models import Administrador
from django.http import HttpResponse,HttpResponseRedirect ,HttpRequest


class PropiedadForm(forms.ModelForm):
	class Meta:
		model = Propiedad
		fields = [
			'idlegal',
			'nombre',
			'direccion',
			'telefono',
			'ciudad',
			# 'administrador',
			'area',
			'tipo',
			'presupuesto_anual',
			'dia_cobro',
			'porcentaje_mora',
			'Imagen',
		]
		labels = {
			'idlegal':'ID-Unico de la propiedad',
			'nombre': 'Nombre',
			'area': 'Area',
			'telefono': 'Telefono',
			'tipo': 'Tipo',
	

		}

		widgets = {
			'nombre':forms.TextInput(attrs={'class':'form-control'}),
			'apellidos':forms.TextInput(attrs={'class':'form-control'}),
			'edad':forms.TextInput(attrs={'class':'form-control'}), 
			'telefono':forms.TextInput(attrs={'class':'form-control'}),
			'email':forms.TextInput(attrs={'class':'form-control'}),
			'domicilio': forms.Textarea(attrs={'class':'form-control'}),
			'presupuesto_anual': forms.TextInput(attrs={'class':'form-control'}),		
			'area': forms.TextInput(attrs={'class':'form-control'}),		
		}


class UnidadForm(forms.ModelForm):
	def __init__(self, *args, **kwargs):
		super(UnidadForm, self).__init__(*args, **kwargs)
		# self.residente = kwargs['request']
		self.request = kwargs['initial']['request']
		propiedad = kwargs['initial']['propiedad']

		# uid= kwargs['initial']['request'].user.id
		uid= self.request.user.id
		self.fields['residente'].queryset = Persona.objects.filter(administrador=uid)
		self.fields['propietario'].queryset = Persona.objects.filter(administrador=uid, propiedad=propiedad)
		self.fields['arrendatario'].queryset = Persona.objects.filter(administrador=uid, propiedad=propiedad, tipo=2)
		# self.fields['propiedad'].queryset = Propiedad.objects.filter(administrador__idu = uid)



	class Meta:
		model = Unidad

		fields = (
			'propiedad',
			'torre',
			'numero',
			'estado',
			'dia_cobro',
			'residente',
			'propietario',
			'arrendatario',
			'responsable',
			'forma_recibo',
			'saldo_favor',
			'porcentaje_mora',
			'valor_mora',
			'coeficiente',
			'valor_pago'

			
		)

		labels = {
			'idlegal':'ID-Unico de la propiedad',
			'nombre': 'Nombre',
			'area': 'Area',
			'telefono': 'Telefono',
			'tipo': 'Tipo',
			'valor_pago':'Valor a Pagar',

		}
		FAVORITE_COLORS_CHOICES = (
			('blue', 'Blue'),
			('green', 'Green'),
			('black', 'Black'),
			)



		vmoratext="Este valor se usara solo una Vez, cuando registre esta unidad"
		widgets = {
			'nombre':forms.TextInput(attrs={'class':'form-control'}),
			'apellidos':forms.TextInput(attrs={'class':'form-control'}),
			'edad':forms.TextInput(attrs={'class':'form-control'}), 
			'telefono':forms.TextInput(attrs={'class':'form-control'}),
			'email':forms.TextInput(attrs={'class':'form-control'}),
			'domicilio': forms.Textarea(attrs={'class':'form-control'}),
			'presupuesto_anual': forms.TextInput(attrs={'class':'form-control'}),		
			'area': forms.TextInput(attrs={'class':'form-control'}),		
			# 'forma_recibo': forms.RadioSelect(),
			# 'residente': forms.Select(attrs={'class':'form-control'}),
			'torre':forms.TextInput(attrs={'class':'xsinput'}),
			'numero':forms.NumberInput(attrs={'class':'xsinput'}),
			'dia_cobro':forms.NumberInput(attrs={'max':31,'class':'xsinput'}),
			'porcentaje_mora':forms.NumberInput(attrs={'max':100,'min':0.0,'step':0.1,'class':'xsinput'}),
			'coeficiente':forms.NumberInput(attrs={'max':100,'min':0.0,'step':0.1})
		,	'valor_mora': forms.NumberInput(attrs={'min':0, 'data-toggle':"tooltip",'data-placement':"right",'title':vmoratext})
		,	'valor_pago': forms.NumberInput(attrs={'min':0})

			# data-toggle="tooltip" data-placement="right" title="Hooray!"

			# 'propiedad': forms.HiddenInput(),
			}
#Validamos que la propiedad nos pertenezca
	def clean_propiedad(self):
		diccionario_limpio = self.cleaned_data
		propiedad = diccionario_limpio.get('propiedad') 
		dato= self.request.POST['propiedad']
		uid = self.request.user.id
		qs=Propiedad.objects.filter(administrador__idu = uid, idlegal=dato)
		# hacemos 2 filtros para comprobar la propiedad,
		# el primero es que la propiedad nos pertenesca y exista
		# el segundo es que la propiedad sea igual a la escrita en la url
		if not (qs) or (dato in self.request.path)==False:
			raise forms.ValidationError("Lo sentimos esta propiedad no esta registrada o está intentado ingresar datos en otra propiedad")

		# if propiedad=="holas" :
		# 	raise forms.ValidationError("El autor debe contener mas de tres caracteres")
		return propiedad

# def __init__(self,*args,**kwargs):
# 	super (UnidadForm,self ).__init__(*args,**kwargs)
# 	uid = self.request.user.id
# 			self.fields['residente'].queryset = Persona.objects.filter(administrador=1)
# 					
# def __init__(self, *args, **kwargs):
# 		super(ProductForm, self).__init__(*args, **kwargs)
# 		self.fields['category'].query_set = Category.objects.filter(filter)


class BancoForm(forms.ModelForm):
	def __init__(self, *args, **kwargs):
		super(BancoForm, self).__init__(*args, **kwargs)
		# self.residente = kwargs['request']
		self.request = kwargs['initial']['requests']

		# uid= kwargs['initial']['request'].user.id
		uid= self.request.user.id
		self.fields['propiedad'].queryset = Propiedad.objects.filter(administrador=uid)
		self.fields['administrador'].queryset = Administrador.objects.filter(idu=uid)

	class Meta:
		model = Banco
		fields = [
			'administrador',
			'banco',
			'num_cuenta',
			'tipo_cuenta',
			'propiedad',

		]
	# def clean_administrador(self):
	# 	diccionario_limpio = self.cleaned_data
	# 	administrador = diccionario_limpio.get('administrador') 
	# 	# dato= self.request.POST['administrador']
	# 	uid = self.request.user.id
	# 	qs=Administrador.objects.filter(idu = uid)
	# 	# a = qs.algo
	# 	if ( administrador in qs):
	# 		raise forms.ValidationError("Lo sentimos esta propiedad no esta registrada o está intentado ingresar datos en otra propiedad")

	# 	# if propiedad=="holas" :
	# 	# 	raise forms.ValidationError("El autor debe contener mas de tres caracteres")
	# 	return administrador


class PersonaForm(forms.ModelForm):
	def __init__(self, *args, **kwargs):
		super(PersonaForm, self).__init__(*args, **kwargs)
		# self.residente = kwargs['request']
		# self.request = kwargs.get('initial').get('requests')
		self.request = kwargs['initial']['requests']
		propiedad = kwargs['initial']['propiedad']
		uid= self.request.user.id
		# self.fields['propiedad'].queryset = Propiedad.objects.filter(administrador=uid,idlegal=propiedad)
		# self.fields['administrador'].queryset = Administrador.objects.filter(idu=uid)

	class Meta:
		model = Persona
		fields = [
			'identificacion',
			'nombre',
			'apellido',
			'email',
			'telefono',
			'celular',
			'tipo',
			# 'propiedad',
			# 'administrador'

		]
	def clean_propiedad(self):
		diccionario_limpio = self.cleaned_data
		propiedad = diccionario_limpio.get('propiedad') 
		dato= self.request.POST['propiedad']
		uid = self.request.user.id
		qs=Propiedad.objects.filter(administrador__idu = uid, idlegal=dato)
		# hacemos 2 filtros para comprobar la propiedad,
		# el primero es que la propiedad nos pertenesca y exista
		# el segundo es que la propiedad sea igual a la escrita en la url
		if not (qs) or (dato in self.request.path)==False:
			raise forms.ValidationError("Lo sentimos esta propiedad no esta registrada o está intentado ingresar datos en otra propiedad")

		# if propiedad=="holas" :
		# 	raise forms.ValidationError("El autor debe contener mas de tres caracteres")
		return propiedad