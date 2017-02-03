from django import forms

from apps.edificios.models import Propiedad, Persona, Unidad, Banco
from apps.usuarios.models import Administrador
from apps.pagos.models import RecibosPagos
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
			'idlegal':forms.TextInput(attrs={'class':'form-control'}),
			'nombre':forms.TextInput(attrs={'class':'form-control'}),
			'apellidos':forms.TextInput(attrs={'class':'form-control'}),
			'edad':forms.TextInput(attrs={'class':'form-control'}), 
			'telefono':forms.NumberInput(attrs={'class':'form-control','min':0,'data-validate-length-range-minmax':"7,20"}),
			'email':forms.EmailInput(attrs={'class':'form-control'}),
			'direccion': forms.TextInput(attrs={'class':'form-control'}),
			'presupuesto_anual': forms.NumberInput(attrs={'class':'form-control'}),		
			'area': forms.NumberInput(attrs={'class':'form-control', 'min':0}),		
			'dia_cobro': forms.NumberInput(attrs={'class':'form-control','min':1,'max':31,'data-validate-minmax':"1,31"}),		
			'ciudad': forms.Select(attrs={'class':'form-control'}),		
			'tipo': forms.Select(attrs={'class':'form-control'}),		
			'porcentaje_mora': forms.NumberInput(attrs={'class':'form-control','min':0,'max':100,'data-validate-minmax':"0,100"}),		
			

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
		Prop = Propiedad.objects.filter(idlegal=propiedad)
		if Prop:
			tipoPro = Prop[0].tipo
			vmoratext="Este Valor no puede ser modificado Debido a que la Propiedad\
						'%s' es Netamente " %(Prop[0].nombre)
			if tipoPro == 1:
				tipoUnidadChoises = (('1', 'Residencial'),)
				vmoratext+="Residencial"
				self.fields['tipo'] = forms.ChoiceField(choices=tipoUnidadChoises, 
                                   widget=forms.Select(attrs={'class':' form-control','readonly':'','data-toggle':"tooltip",'data-placement':"right",'title':vmoratext}))
			elif tipoPro == 2:
				tipoUnidadChoises = (('2', 'Comercial'),)
				vmoratext+="Comercial"
				self.fields['tipo'] = forms.ChoiceField(choices=tipoUnidadChoises, 
                                   widget=forms.Select(attrs={'class':' form-control','readonly':'','data-toggle':"tooltip",'data-placement':"right",'title':vmoratext}))
			elif tipoPro == 3:
				tipoUnidadChoises = (('1', 'Residencial'),('2', 'Comercial'))
				self.fields['tipo'] = forms.ChoiceField(choices=tipoUnidadChoises, 
                                   widget=forms.Select(attrs={'class':' form-control','enabled':'enabled'}))
		# tipoUnidad = (('1', 'Residencial'),('2', 'Comercial'))
		# self.fields['tipo'] = forms.ChoiceField(choices=tipoUnidad, 
                                   # widget=forms.Select(attrs={'disabled':'disabled'}))

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
			'valor_pago',
			'tipo',

			
		)

		labels = {
			'idlegal':'ID-Unico de la propiedad',
			'nombre': 'Nombre',
			'area': 'Area',
			'telefono': 'Telefono',
			'tipo': 'Tipo',
			'valor_pago':'Valor a Pagar',
			'tipo':'Tipo Unidad',
			'valor_mora':'saldo en mora',
			'dia_cobro':'Dia de Facturacion',

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
			'propietario': forms.Select(attrs={'class':'form-control'}),
			'arrendatario': forms.Select(attrs={'class':'form-control'}),
			'responsable': forms.Select(attrs={'class':'form-control'}),
			'forma_recibo': forms.Select(attrs={'class':'form-control'}),
			'saldo_favor': forms.NumberInput(attrs={'class':'form-control'}),

			'torre':forms.TextInput(attrs={'class':' form-control'}),
			'numero':forms.NumberInput(attrs={'class':' form-control'}),
			'dia_cobro':forms.NumberInput(attrs={'max':31,'class':' form-control'}),
			'porcentaje_mora':forms.NumberInput(attrs={'max':100,'min':0.0,'step':0.1,'class':' form-control'}),
			'coeficiente':forms.NumberInput(attrs={'max':100,'min':0.0,'step':0.1,'class':'form-control'})
		,	'valor_mora': forms.NumberInput(attrs={'min':0,'class':'form-control', 'data-toggle':"tooltip",'data-placement':"right",'title':vmoratext})
		,	'valor_pago': forms.NumberInput(attrs={'min':0,'class':'form-control'}),
			'estado': forms.Select(attrs={'class':'form-control'}),

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

	def clean_numero(self):
		diccionario_limpio = self.cleaned_data
		numero = diccionario_limpio.get('numero') 

		formtorre = self.request.POST['torre']
		formnumero = self.request.POST['numero']
		propiedad= self.request.POST['propiedad']
		uid = self.request.user.id
		qs=Unidad.objects.filter(propiedad__idlegal=propiedad,\
								propiedad__administrador__idu = uid,\
								torre=formtorre, numero=formnumero)
								# si existe un valor en la consulta
		if qs :
			if "edit" in self.request.path:
				return numero
			else:
				raise forms.ValidationError("novalido")

		# if propiedad=="holas" :
		# 	raise forms.ValidationError("El autor debe contener mas de tres caracteres")
		return numero
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
		widgets = {
			'banco': forms.TextInput(attrs={'class':'form-control'}),
			'num_cuenta': forms.TextInput(attrs={'class':'form-control'}),
			'tipo_cuenta': forms.Select(attrs={'class':'form-control'}),
			'propiedad': forms.Select(attrs={'class':'form-control'}),



		}
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


class  PagoForm(forms.ModelForm):
	class Meta:
		model = RecibosPagos
		fields = [
			'unidad',
			'no_comprobante',
			'pagador',
			'suma',
			'enletras',
			'concepto',
			'forma_pago',
			'referencia1',
			'referencia2',
			'recibo',
			'tipo',
		]