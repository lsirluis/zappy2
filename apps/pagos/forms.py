from django import forms
from functools import partial
# DateInput = partial(forms.DateInput, {'class': 'datepicker'})
forms.DateInput(format='%m/%d/%Y' )
# from apps.edificios.models import Propiedad, Persona, Unidad, Banco
# from apps.usuarios.models import Administrador
from django.http import HttpResponse,HttpResponseRedirect ,HttpRequest
from apps.pagos.models import Recibo , Detalle

class ReciboForm(forms.ModelForm):
	fecha_vencimiento = forms.DateField(label=("fecha_vencimiento"), 
                                  initial=None,
                                  required=True, 
                                  input_formats=['%d/%m/%Y'],
								widget=forms.DateInput(format = '%d/%m/%Y', attrs= {'class': 'datepicker mdinput','placeholder':'Dia / Mes / Año"'}))

	class Meta:
		model = Recibo
		fields = [
			'descripcion',
			'unidad',
			'fecha_cobrada',
			'fecha_vencimiento',
		
		]
		labels = {
			'fecha_cobrada': 'Fecha a cobrar',
			'fecha_vencimiento':'fecha_vencimiento',

		}
	
		# fecha_vencimiento = 
		widgets = {
			'nombre':forms.TextInput(attrs={'class':'form-control'}),
			'apellidos':forms.TextInput(attrs={'class':'form-control'}),
			'edad':forms.TextInput(attrs={'class':'form-control'}), 
			'telefono':forms.TextInput(attrs={'class':'form-control'}),
			'email':forms.TextInput(attrs={'class':'form-control'}),
			'domicilio': forms.Textarea(attrs={'class':'form-control'}),
			'presupuesto_anual': forms.TextInput(attrs={'class':'form-control'}),		
			'area': forms.TextInput(attrs={'class':'form-control'}),	
			# 'fecha_vencimiento': forms.DateInput(attrs= {'class': 'datepicker mdinput','placeholder':'Dia / Mes / Año"'}),
			'fecha_cobrada': forms.DateInput(format='%d/%m/%Y',attrs= {'class': 'datepicker mdinput ','placeholder':'Dia / Mes / Año"'}),

		}

class DetalleForm(forms.ModelForm):
	class Meta:
		model = Detalle
		fields = [
			'descripcion',
			'valor',
			'tipo',
		
		]
		labels = {
			'fecha_cobrada': 'Fecha a cobrar',
		

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