from django.shortcuts import render
from django.utils.six.moves import zip_longest 
from django.core.urlresolvers import reverse_lazy
from django.urls import reverse
from django.http import HttpResponse,HttpResponseRedirect ,HttpRequest
import datetime
import calendar
import json
from django.db.models import Q


# generic views
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
# models
from apps.pagos.models import Recibo , Detalle, Noticia, DeNoticia \
							  ,Deuda , RecibosAuto, RecibosPagos\
							  ,CuotaExtraordinaria,CuotaExtraUnidad
from apps.edificios.models import Unidad, Propiedad,Banco
from apps.usuarios.models import Administrador

# funcion de edificios
from django.contrib import messages
# forms
from apps.pagos.forms import ReciboForm, DetalleForm, CuotaextraForm


# Create your views here.
def ReciboLists(request, id_propiedad, pk):

	contexto = {'propiedades': "hola",'messages':["hola"],'title':"nuevotitulo"}
	# return render(request, 'Propiedad/Propiedad_List.html',contexto)
	return render(request, 'Pagos/Factura_list.html',contexto)


class ReciboList(ListView):
	model = Recibo
	template_name = 'Pagos/Factura_list.html'	
	def get_context_data(self, *args,**kwargs):
		context = super(ReciboList, self).get_context_data(*args,**kwargs)
		uid = self.request.user.id
		idpro = self.kwargs.get('id_propiedad',0)
		pkunidad= self.kwargs.get('pk',0)
		if EsMiPropiedad(uid, idpro):
			
			if EsMiUnidad(uid, idpro, pkunidad):
				context['DatosUnidad']= Unidad.objects.filter(id=pkunidad, propiedad=idpro, propiedad__administrador=uid)[0]	

				context['title']= ("Facturas en la Torre : "+(context['DatosUnidad'].torre)+" - Apto : "+(str(context['DatosUnidad'].numero))+"")
				context['breadurl']=[{'nombre':'Propiedades','url':"Propiedad:Solicitud_listar"},\
								 {'nombre':context['DatosUnidad'].propiedad.nombre,'url':"Propiedad:Solicitud_apartamentos",'arg':context['DatosUnidad'].propiedad.idlegal},{'nombre':context['title'],'url':"j"}]
				context['Uestado']=EnDeudaApartamento(context['DatosUnidad'])
				if (Recibo.objects.filter(unidad=pkunidad,unidad__propiedad=idpro, unidad__propiedad__administrador__idu = uid)):
					context['object_list']= Recibo.objects.filter(unidad=pkunidad, unidad__propiedad=idpro, unidad__propiedad__administrador__idu = uid)
					
				else:
					context['object_list']=""
					# context['title']= "No tiene"
					messages.add_message(self.request, messages.ERROR, 'Lo sentimos, No hay ningun recibo que mostrar!')

			else:
				context['propiedad']=idpro
				context['title']= "Unidad no encontrada"
				messages.add_message(self.request, messages.ERROR, 'Lo sentimos, Unidad no esta Registrada')

		else:
			context['title']= "Propiedad no encontrada"
			messages.add_message(self.request, messages.ERROR, 'Lo sentimos, Propiedad no esta Registrada')


		# context['variable1']=idpro
		# context['variable2']=pkunidad
		return context
def EnDeudaApartamento(apartamento):
	lista=[]
	# for apartamento in apartamentos:
	recibos = Recibo.objects.filter(unidad=apartamento.id,estado=0)
	if recibos or apartamento.valor_mora>0 :
		lista.append(True)
	else:
		lista.append(False)
		# lista.append(apartamento.id)
	# al final retorno la lista del estado de deuda (si, no), de apartamentos
	return lista

class DetalleFactura(ListView):
	model = Detalle
	template_name = 'Pagos/DetalleFactura.html'
	def get_context_data(self, *args,**kwargs):
		context = super(DetalleFactura, self).get_context_data(*args,**kwargs)
		uid = self.request.user.id
		idpro = self.kwargs.get('id_propiedad',0)
		pkunidad= self.kwargs.get('pk',0)
		factura = self.kwargs.get('factura',0)
		# realizamos la consulta para obtener el detalle de la factura
		qs= Detalle.objects.filter(idRecibo__unidad__propiedad__administrador=uid, idRecibo= factura, idRecibo__unidad=pkunidad, idRecibo__unidad__propiedad = idpro)
		context['object_list']= qs
		context['DatosUnidad']= Unidad.objects.filter(id=pkunidad, propiedad=idpro, propiedad__administrador=uid)[0]	
		
		context['banco']=Banco.objects.filter(propiedad=idpro)
		# sino hay detalles
		if not qs :
			messages.add_message(self.request, messages.ERROR, 'Lo Sentimos no hay detalles para esta factura')
		# si hay detalles calculamos su deuda
		else:
			recibo= Recibo.objects.filter(id=factura)
			if recibo:
				context['deudas']=Deudaxrecibo(recibo[0])


		context['title'] = "Detalle de Factura"
		aux = ("Facturas en la Torre : "+(context['DatosUnidad'].torre)+" - Apto : "+(str(context['DatosUnidad'].numero))+"")
		context['breadurl']=[{'nombre':'Propiedades','url':"Propiedad:Solicitud_listar"},\
							 {'nombre':context['DatosUnidad'].propiedad.nombre,'url':"Propiedad:Solicitud_apartamentos",'arg':context['DatosUnidad'].propiedad.idlegal},\
							 {'nombre':aux,'url':"Propiedad:Solicitud_appagos",'arg':context['DatosUnidad'].propiedad.idlegal,'arg2':context['DatosUnidad'].id},\
							 {'nombre':context['title']}]

		return context

class FacturaCreate(CreateView):
	model = Detalle
	form_class = ReciboForm
	second_form_class= DetalleForm

# al que llaman es el segundo modelo
	template_name = 'Pagos/Factura_form.html'
	success_url = reverse_lazy('Propiedad:Solicitud_listar')

	# success_url =reverse_lazy('Propiedad:Solicitud_appagos',args=[self.a,self.b])
	# def get_initial(self):
		# self.initial.update({ 'requests': self.request})
		# return self.initial

	def get_context_data(self, **kwargs):
		context = super(FacturaCreate, self).get_context_data(**kwargs)
		uid = self.request.user.id
		idpro = self.kwargs.get('id_propiedad',0)
		pkunidad= self.kwargs.get('pk',0)
		factura = self.kwargs.get('factura',0)
		context['title'] = "Crear Factura "
		# si la propiedad es mia y la unidad es mia mostramos form factura
		if EsMiPropiedad(uid, idpro):
			# si llega aqui significa que la propiedad es mia
			# ahora comprobaremos si la unidad es mia y pertenece a esa propiedad
			if EsMiUnidad(uid, idpro,pkunidad):
			# si llega aqui significa que la propiedad y la unidad son mios
				context['DatosUnidad']= Unidad.objects.filter(id=pkunidad, propiedad=idpro, propiedad__administrador=uid)[0]	
				if 'form' not in context:
					context['form']= self.form_class(self.request.GET)
				if 'form2' not in context:
					context['form2']= self.second_form_class(self.request.GET)
				nombrepro=context['DatosUnidad'].propiedad.nombre
				aux = ("Facturas en la Torre : "+(context['DatosUnidad'].torre)+" - Apto : "+(str(context['DatosUnidad'].numero))+"")
				context['breadurl']=[{'nombre':'Propiedades','url':"Propiedad:Solicitud_listar"},\
							{'nombre':nombrepro,'url':"Propiedad:Solicitud_apartamentos",'arg':idpro},\
							{'nombre':aux,'url':'Propiedad:Solicitud_appagos','arg':idpro,'arg2':pkunidad},\
							{'nombre':context['title']}]
				temprecibo = Recibo.objects.filter(unidad=pkunidad).order_by("-numConsecutivo")
				if temprecibo:
					Consecutivo = temprecibo[0].numConsecutivo + 1
				else:
					Consecutivo = 1
				context['consecutivo']=	Consecutivo

			else:
				messages.add_message(self.request, messages.ERROR, 'Lo sentimos esta unidad no Existe!')
		else: 
			messages.add_message(self.request, messages.ERROR, 'Lo sentimos esta Propiedad no Existe!')

		
		return context

	def post(self, request, *args, **kwargs):
		self.object = self.get_object
		descripcion = request.POST.getlist('descripcion')
		valor = request.POST.getlist('valor')
		interes = request.POST.getlist('interes')
		total = request.POST.getlist('total')
		detalles = zip_longest(descripcion,valor,interes,total,"")
		detalles = list(detalles)

		# if len(descripcion)>len(valor):
			# contador = len(descripcion)
		# else:
			# contador = len(valor)

		tipo = "Pago"

		form = self.form_class(request.POST)
		form2 = self.second_form_class(request.POST)

		uid = self.request.user.id

		if form.is_valid() and form2.is_valid():
			# primero guardaremos el recibo y posteriormente los detalles
			fecha_cobrada=request.POST.get('fecha_cobrada')
			fecha_vencimiento=request.POST.get('fecha_vencimiento')
			
			idpro = self.kwargs.get('id_propiedad',0)
			pkunidad= self.kwargs.get('pk',0)
			if request.POST['unidad']:
				if request.POST['unidad'] == pkunidad :
					if EsMiPropiedad(uid, idpro):
						if EsMiUnidad(uid, idpro, pkunidad):
# si llega aqui sognifica que exite un post unidad, la propiedad es mia y
# la unidad pertenece a esa propiedad
							temprecibo = Recibo.objects.filter(unidad=pkunidad).order_by("-numConsecutivo")
							if temprecibo:
								Consecutivo = temprecibo[0].numConsecutivo + 1
							else:
								Consecutivo = 1
							unidad = Unidad.objects.get(propiedad=idpro,id= pkunidad, propiedad__administrador= uid)
						# sirve
							recibo =form.save(commit=False)
							recibo.estado =0
							recibo.numConsecutivo=Consecutivo
							recibo.descripcion="Factura Manual"
							recibo.save()
							contador = 0
							for datos in detalles:
								# detalle = form2.save(commit=False)
								# detalle.idRecibo = recibo
								# detalle.valor = datos[1]
								# detalle.tipo= tipo
								# detalle.descripcion=datos[0]
								# detalle.save()
								Detalles = Detalle(valor=(datos[1]), tipo= tipo, descripcion=datos[0], idRecibo = recibo )
								Detalles.save()
								contador=contador+1
						# fin sirve
							# recibo = Recibo(estado=1,descripcion='Pago', numConsecutivo=1, fecha_cobrada=fecha_cobrada, unidad=unidad, fecha_vencimiento=fecha_vencimiento)
							# recibo.save()
							# for datos in detalles:
							# 	Detalles = Detalle(valor=(datos[1]), tipo= tipo, descripcion=datos[0], idRecibo = recibo )
							# 	Detalles.save()
			# for x in xrange(1,10):
				# pass
			# solicitud = form.save(commit=False)
			# solicitud.persona = form2.save()
			# solicitud.save()		
							# return HttpResponse(contador)
							messages.add_message(self.request, messages.SUCCESS, 'Factura Añadida satisfactoriamente!')
							self.success_url = reverse_lazy('Propiedad:Solicitud_appagos',args=[idpro,pkunidad])
							return HttpResponseRedirect(self.get_success_url())


						else:
							messages.add_message(self.request, messages.ERROR, 'Lo sentimos esta unidad no Existe!')
							return self.render_to_response(self.get_context_data(form=form,form2=form2,detalles=detalles))
					else:
						messages.add_message(self.request, messages.ERROR, 'Lo sentimos esta Propiedad no Existe!')
						return self.render_to_response(self.get_context_data(form=form,form2=form2,detalles=detalles))
				else:
					messages.add_message(self.request, messages.ERROR, 'Por favor no modifique los datos, Gracias!!')
					return self.render_to_response(self.get_context_data(form=form,form2=form2,detalles=detalles))
			else:
				messages.add_message(self.request, messages.ERROR, 'Por favor no modifique la unidad!')
				return self.render_to_response(self.get_context_data(form=form,form2=form2,detalles=detalles))

				

		else:
			return self.render_to_response(self.get_context_data(form=form,form2=form2,detalles=detalles))
			# return self.render_to_response(self.get_context_data(form=form,form2=form2,descripcion=descripcion))


def EsMiPropiedad(idadmin, idpro):
	if Propiedad.objects.filter(administrador=idadmin, idlegal= idpro) :
		return True
	return False;

def EsMiUnidad(idadmin, idpro, idunidad):
	if Unidad.objects.filter(propiedad=idpro,id= idunidad, propiedad__administrador= idadmin) :
		return True
	return False;

def probar(request):
	return HttpResponseRedirect(reverse_lazy('Propiedad:Solicitud_appagos',args=[1945,1928]))

# a continuacion metodos para hacer la generacion de facturas

# inicio 1 metodo para facturas por dia global
# **************************************************************************
def fechaActual():
	fecha = datetime.datetime.now()
	ahora = "%s-%s-%s" % (fecha.year, fecha.month, fecha.day)
	return ahora

	# da la fecha completa con tiempo, pero puede fraccionarce
def fechaparcial():
	fecha = datetime.datetime.now()
	return fecha

	#este calulara la fecha anterior para generar un recibo a un mes pasado 
def fechamesanterior():
	fecha = datetime.datetime.now()
	# si la fecha del servidor es enero, entonces se cambia la fecha
	# a un ano anterior, esto para que cuando se quiera cobrar en enero
	# lo de diciembre del ano pasado, no se combre diciembre del presente ano
	# ademas, siempre se cobra un mes anterior al presente
	if fecha.month == 1:
		anterior = "%s-%s-%s" % (fecha.year-1, 12, fecha.day)
	else:
		anterior = "%s-%s-%s" % (fecha.year, fecha.month-1, fecha.day)
	return anterior

	# este a la fecha actual le agregara 5 dias, significa que en
	# 5 dias se vence la factura y empieza a cobrar intereses
	# aqui el problema es saber primero el ultmo da del mes
def fechavencimiento():
	fecha = datetime.datetime.now()
	cantdias = calendar.monthrange(fecha.year,fecha.month)[1]
	# si supera la cantdad del dia del mes, entonces el vencimiento se
	# pasa al siguiente mes
	if (fecha.day+5) > cantdias:
		temp = (fecha.day+5) - cantdias
		# ahora, si es diciembre el vencimiento sera en enero
		if fecha.month == 12 :
			vencimiento = "%s-%s-%s" % (fecha.year+1, 1, temp)
		else :
			vencimiento = "%s-%s-%s" % (fecha.year, fecha.month+1, temp)
	else:
			vencimiento = "%s-%s-%s" % (fecha.year, fecha.month, fecha.day+5)

	return vencimiento


	# este calculara la cuota mensual,servira para compararla con la
	# que se calculo al registrar la propiedad
def calulototal(presu,coef):
	calculo = presu * (coef/100)
	return calculo


	# P*******************************************************************
	# inicio generadorglobal
def GenerardorGlobal(request):
	# unidad = Unidad.objects.filter(id=41)
	unidades = Unidad.objects.all()

	if unidades:

		# return HttpResponse("<h1>Si se encontro la unidad = %s </h1>" %unidad[0].id)
		# recibo = Recibo.objects.filter(id=2)
		# if recibo:
			# return HttpResponse("Si se encontro resibo")
		# if fechaActual() == str(recibo[0].fecha_cobrada):
			# resultado = "si concuerdan"
		# else:
			# resultado = "no concuerdan"
		# return HttpResponse()
		# return HttpResponse("Fecha del recibo = %s y la fecha del servidor es %s y las 2 fechas = %s</h1>" %(recibo[0].fecha_cobrada, fechaActual(), resultado))
		# return HttpResponse("<h1>Si hay unidades</h1>")

		contador = 0
		dia = fechaparcial().day
		for dato in unidades:
			# si el dia de cobro es igual al dia actual procedemos
			# a realizar la factura a la unidad en cuestion
			if dato.dia_cobro == dia:
				# ahora preguntamos si el recibo existe, pues no queremos 
				# repetidos en una unidad
				# if pendiente
				contador = contador + 1
				# la deuda inicial es la deuda en mora que se puso
				# al registrar esta unidad, por lo general se usa 1 vez
				if dato.valor_mora :
					
					deudainicial = dato.valor_mora

				else:
					deudainicial = 0

				# la deudamora es la deuda que se acumula por el no 
				# pago de las facturas pasadas
				# deudamora = funcioncalcularamora()
				# anadidos = funcioncalcularaanadidos

				# ahora vemos si en la unidad tiene un valor de pago
				# este valor de pago se pone al inicio
				# pero puede haber casos en la que este valor es cero o nulo
				# y debemos calcular el costo con el presupuesto y coeficiente
				valorPago = dato.valor_pago
				if valorPago<=0:
					valorPago= calulototal(dato.propiedad.presupuesto, dato.coeficiente)

				deudatotal = deudainicial + valorPago
				recibo = Recibo(
				estado =1,
				numConsecutivo=1,
				descripcion="Recibo-Mensual",
				fecha_generacion = fechaparcial(),
				fecha_cobrada = fechamesanterior(),
				unidad = dato,
				fecha_vencimiento = fechavencimiento(),
				)
				recibo.save()

				Detalles = Detalle(valor=deudatotal, tipo="Pago", descripcion="Pago-Administracion", idRecibo = recibo )
				Detalles.save()
			
		return HttpResponse("se realizo la factura a %s unidades" %(contador))
	
	else:
		return HttpResponse("No Hay unidades")

# Fin GeneradorGlobal
# inicion pruebagenerador
def pruebagenerador(request):
	administradores = Administrador.objects.all()
	contador = 0
	if administradores:
		for admin in administradores:
			contador = contador + GenEdificioUnidad(admin)
		return HttpResponse("Actualizacion exitosa, Unidades Actualizadas \
							%s "% contador)
	else:
		return HttpResponse("No Hay Administradores Registrados")

#fin pruebagenerador

# Inicio GenEdificioUnidad
# este metodo hara 
def GenEdificioUnidad(Userid):
	# si el administrador existe
	# quitar el siguiente si, para hacerlo mas optimo
	contador = 0
	if Administrador.objects.filter(idu=Userid):
		# entonces buscamos sus edificios
		edificios = Propiedad.objects.filter(administrador=Userid)
		# si tiene edificios
		if edificios:
			# ya teniendo los edificios de este administrador
			# para cada edificio
			for edifi in edificios:
				noticia = GeneradorNotifia(Userid,edifi)
				# ahora buscamos las unidades
				unidades = Unidad.objects.filter(propiedad=edifi.idlegal, propiedad__administrador = (Userid))
				
				# si hay unidades
				if unidades:
					# ahora ya tenemos las unidades en ese edificio
					# for unidad in unidades:
					# ahora mandamos las unides
					# Ahora haremos la lista de uactualizados
					contador =contador + GeneradorDatosUnid(unidades,noticia)
	return contador

# fin GenEdificioUnidad

# inicio generadorDatosfact
def GeneradorDatosUnid(unidades,noticia):
	contador = 0
	dia = fechaparcial().day
	for unidad in unidades:
		# si el dia de cobro es igual al dia actual procedemos
		# a realizar la factura a la unidad en cuestion
		if unidad.dia_cobro == dia:
			# la deuda inicial es la deuda en mora que se puso
			# al registrar esta unidad, por lo general se usa 1 vez
			# guardamos la noticia, se guarda aqui para que no se creen
			# noticias cuando no se generara ningun recibo 
			if unidad.valor_mora :					
					deudainicial = unidad.valor_mora
			else:
				deudainicial = 0

			# la deudamora es la deuda que se acumula por el no 
			# pago de las facturas pasadas
			# deudamora = funcioncalcularamora()
			# anadidos = funcioncalcularaanadidos
			# ahora vemos si en la unidad tiene un valor de pago
			# este valor de pago se pone al inicio
			# pero puede haber casos en la que este valor es cero o nulo
			# y debemos calcular el costo con el presupuesto y coeficiente
			valorPago = unidad.valor_pago
			if valorPago<=0:
				valorPago= calulototal(unidad.propiedad.presupuesto, unidad.coeficiente)

			deudatotal = deudainicial + valorPago
			# procedemos a guardar la factura y sus detalles
			factura = SaveFacturaDetalles(unidad ,deudatotal)
			if factura :
				noticia.save()
				contador = contador + 1
				GeneradordetalleNotifia(noticia, unidad, factura)
	return contador
# fin generadorDatosfact

# Inicio SaveFacturaDetalles()
def SaveFacturaDetalles(pkunidad,valor):
	temprecibo = Recibo.objects.filter(unidad=pkunidad.id).order_by("-fecha_generacion")
	if temprecibo:
		Consecutivo = temprecibo[0].numConsecutivo + 1
	else:
		Consecutivo = 1

	recAuto = RecibosAuto.objects.filter(idRecibo__unidad=pkunidad \
										,idRecibo__fecha_cobrada = fechamesanterior())
	# si me devuelve un recibo significa que existe un recibo para
	# esa fecha, entonces no creamos un nuevo recibo porque ya existe
	# if not recAuto or recAuto:
	if not recAuto :

		recibo = Recibo(
			# 0 indica que esta en deuda, 1 que se pago
					estado =1,
					numConsecutivo=Consecutivo,
					descripcion="Recibo-Mensual",
					fecha_generacion = fechaparcial(),
					fecha_cobrada = fechamesanterior(),
					unidad = pkunidad,
					fecha_vencimiento = fechavencimiento(),
					)
		recibo.save()

		# como este recibo es automatico vamos a guardar la cuota de Aminstracion
		Detalles = Detalle(valor=valor, tipo="Pago", descripcion="Pago-Administracion", idRecibo = recibo )
		Detalles.save()

#INICIO CUOTA EXTRA 
		# procedemos a ver si la propiedad tiene cuota extraordinaria
		cuotasextras = CuotaExtraordinaria.objects.filter(propiedad= pkunidad.propiedad.idlegal, estado=1)
		# si tenemos extraordinaria procedemos a agregarla en los detalles
		if cuotasextras:
			for cuotaextra in cuotasextras:
				unidadextra = CuotaExtraUnidad.objects.filter(idExtraordinaria = cuotaextra.id\
													, unidad= pkunidad.id, idExtraordinaria__estado=1, cont_cuota__lt=cuotaextra.cuotas)
				if unidadextra: # si la unidad presenta una cuota
					val = unidadextra[0].valor
					descripcion = str("Cuota-Extraordinaria(id:"+str(cuotaextra.id)+") cuota: #"+str(unidadextra[0].cont_cuota+1))
					Detalles = Detalle(valor=val, tipo="Pago", descripcion=descripcion, idRecibo = recibo )
					Detalles.save()
					unidadextra[0].cont_cuota = unidadextra[0].cont_cuota + 1
					unidadextra[0].save()

				# ahora comprobaremos si ya todas las unidades tienen esa cuota extra
				# primero obtenemos la cantidad de unidades
				cantunidades = CuotaExtraUnidad.objects.filter(idExtraordinaria = cuotaextra.id).count()
				# ahora obtenemos las unidades que su cont_cuota es igual a la cuota extra
				fincuotas = CuotaExtraUnidad.objects.filter(idExtraordinaria = cuotaextra.id, cont_cuota__gte=cuotaextra.cuotas).count()
				# si son iiguales significa que todas las unidades han resibido todas
				# las cuotas que les correspondian de las cuotas extraordinarias 
				if fincuotas >= cantunidades:
					cuotaextra.estado=0
					cuotaextra.save()
# FIN CUOTA EXTRA


				# if cuotaextra.tipo_cuota == 0:
				# 	cantidadunidades = Unidad.objects.filter(propiedad=pkunidad__propiedad.idlegal).count()
				# 	val = cuotaextra.valor / cantidadunidades
				# 	Detalles = Detalle(valor=val, tipo="Pago", descripcion="Cuota-Extraordinaria", idRecibo = recibo )
				# 	Detalles.save()
				# else:   #para cuando es por coeficiente	
				# 	val = pkunidad.coeficiente * cuotaextra.valor
				# 	Detalles = Detalle(valor=val, tipo="Pago", descripcion="Cuota-Extraordinaria", idRecibo = recibo )
				# 	Detalles.save()
		# inicio metodo2
		
		# ahora vamos a buscar los recibos en deuda de esta unidad
		# ordenamos del mas viejo primero
		RecibosDeudas = Recibo.objects.filter(unidad=pkunidad, estado=0).order_by('fecha_generacion')
		# ya tenemos los recibos ahora a cada recibo le vamos a sacar su valor
		for recibodeuda in RecibosDeudas:
			deuda = Deuda(
				tipo="deuda",
				IdReciboDeuda=recibodeuda,
				idDetalle = Detalles,
				unidad=pkunidad,

				)
			deuda.save()
				
		recibo.estado=0
		recibo.save()
		
		pkunidad.valor_mora=0
		pkunidad.save()	

		reciboauto = RecibosAuto(
			idRecibo=recibo
			)
		reciboauto.save()

		return recibo
		# fin metodo 2


		# ahora vamos a ver si esta unidad posee deusas, si es asi se calculara el valor
		deuda = DeudaUnidad(pkunidad)
		recibo.estado=0
		recibo.save()
		# si hay una deuda por recibos anteriores, se crea un nuevo detalle
		if deuda>0:
			Detalles = Detalle(valor=deuda, tipo="Pago", descripcion="Deuda", idRecibo = recibo )
			Detalles.save()


		return recibo

# Fin SaveFacturaDetalles()5

# INICIO DEUDA
def Deudaxrecibo(recibo):
	listafacturas=[]
	# la forma [{"factura":factura, "Detalles":[]}]
	# fechalimite=recibo.fecha_cobrada
	fechalimite=recibo.fecha_generacion

	# obtenemos las facturas sin pagar anteriores a esta
	# facturas = Recibo.objects.exclude(id=recibo.id).filter(estado=0,unidad= recibo.unidad, fecha_cobrada__lte=fechalimite)
	facturas = Recibo.objects.exclude(id=recibo.id).filter(estado=0,unidad= recibo.unidad, fecha_generacion__lte=fechalimite)

	# por cada factura obtenemos sus detalles
	if facturas:
		for factura in facturas:
			detalles = Detalle.objects.filter(idRecibo=factura.id)
			if detalles:
				costo=0
				for detalle in detalles:
					costo = costo+detalle.valor
				dato={"Factura":factura, "detalles":detalles,"costo":costo}
				listafacturas.append(dato)
	return listafacturas



# FIN DEUDA



# INICIO DeudaUnidad() ---- no se esta usando
def DeudaUnidad(pkunidad):
	mora=0
	RecibosMora = Recibo.objects.filter(unidad=pkunidad, estado=0).order_by('-fecha_generacion')
	# for recibo in RecibosMora:
	# si hay un recibo vencido entonces(el ultimo generado),
	# procedemos a buscar sus detalles

	if RecibosMora:
		detalles = Detalle.objects.filter(idRecibo=RecibosMora[0].id)
		deuda = 0
		for detalle in detalles:
			deuda = deuda + detalle.valor
		# return HttpResponse("esta unidad posee una deuda de %s "\
							 # % deuda)
	# return HttpResponse("No hay Recibos vencidos")
		return deuda
	return 0

# FIN DeudaUnidad


# Inicio GeneradorNotifia()
def GeneradorNotifia(admin,edifi):
	noticia = Noticia(
				administrador = admin,
				estado =0,
				descripcion="GeneradoAuto",
				propiedad=edifi
				)
	# noticia.save()
	return noticia

def GeneradordetalleNotifia(noticia, pkunidad,recibo):	
	detalle = DeNoticia(
				idNoticia = noticia,
				unidad =pkunidad,
				idRecibo=recibo,
				)
	detalle.save()

class NoticiaList(ListView):
	model= Noticia
	template_name = 'Pagos/Notificaciones_list.html'

	def get_context_data(self, **kwargs):
		context = super(NoticiaList, self).get_context_data(**kwargs)
		uid = self.request.user.id
		noticias= Noticia.objects.filter(administrador = uid)
		Lista=[]
		for noticia in noticias:
			det = DeNoticia.objects.filter(idNoticia= noticia.id)
			dato={'Noticia':noticia,'Detalles':det}
			Lista.append(dato)
		context['Noticias']=Lista
		context['title']= "Noticias | Zappy"
		return context# Fin GeneradorNoticia

# fin inicio 1





# INICIO CARTERA

class CarteraList(ListView):
	model = Recibo
	template_name = "Pagos/Cartera_List.html"
	def get_context_data(self, **kwargs):
		context = super(CarteraList, self).get_context_data(**kwargs)
		uid = self.request.user.id
		idpro = self.kwargs.get('id_propiedad',0)
		if EsMiPropiedad(uid,idpro):
			propiedad = Propiedad.objects.filter(idlegal = idpro)
			context['title'] = "Cartera en la Propiedad: "+propiedad[0].nombre
			# buscara los recibos no pagados de esta propiedad
			recibos = Recibo.objects.filter(estado=0\
											,unidad__propiedad = propiedad[0].idlegal).order_by('unidad_id')
			
			lista = listaUdeudas(recibos)
			context['object_list'] = recibos
			context['milista']=lista

		else:
			context['title'] = "No hay datos que  mostrar"
			context['object_list']=""
		return context
# FIN CARTERA
def listaUdeudas(recibos):
	lista=[] # lista
	if recibos :
		unidad = recibos[0].unidad # obtenemos unidad del recibo
		RECIBOS = []
		COSTO=0 # costo de todas los detalles de esa unidad
		for recibo in recibos:
			# buscamos los detalles en cada recibo de la unidad
			detalles = Detalle.objects.filter(idRecibo=recibo.id)
			RECIBO = {'recibo':recibo, 'detalles':detalles}
			# procedemos a sacar los costos
			CostoTemp = 0
			for detalle in detalles:
				CostoTemp = CostoTemp + detalle.valor
			# for detalle in detalles:
			if recibo.unidad == unidad :
				RECIBOS.append(RECIBO)
				COSTO = COSTO + CostoTemp
			else:
				dato = {'unidad':unidad,'recibos':RECIBOS,"costo":COSTO}
				lista.append(dato)
				RECIBOS = []
				COSTO=CostoTemp
				RECIBOS.append(RECIBO)
				unidad = recibo.unidad
		# esta parte garantiza que cuando se es el ultimo ciclo
		# se agrege a la lista, caso contrario no lo haria
		# para la ultima unidad
		dato = {'unidad':unidad,'recibos':RECIBOS,"costo":COSTO}		
		lista.append(dato)	
	return lista

# a continuacion se hara un metodo que retorne una lista de recibos 
# en deuda y seguido de su costo en el siguiente formato
# lista[ {'recibo':recibo, 'costo': costo},... ]
# el costo incluye sus detalles y sus deudas
def listaReciboCosto(unidadid):
	lista=[] # lista
	# obtenemos los recibos en mora de esa unidad
	recibos = Recibo.objects.filter(Q(estado=0\
					,unidad=unidadid) | Q(estado=2\
					,unidad=unidadid) ).\
					order_by('fecha_generacion')
	# teniendo todos los recibos vencidos.a uno por uno le 
	# obtenemos los recibos anteriores al actual y el actual
	for recibo in recibos:
		# obtenemos el costo del actualrecibo 
		# costo = 0
		# luego de tener el costo del actual recibo, 
		# recibosAnt = Recibo.objects.exclude(id=recibo.id).filter(estado=0,unidad= recibo.unidad, fecha_generacion__lte=recibo.fecha_generacion)
		# obtenemos los
		recibosAntyAct = Recibo.objects.filter(Q(estado=0,unidad= recibo.unidad, fecha_generacion__lte=recibo.fecha_generacion) |\
											   Q(estado=2,unidad= recibo.unidad, fecha_generacion__lte=recibo.fecha_generacion))
		costo = 0
		# por cada factura obtenemos sus detalles
		if recibosAntyAct:
			for factura in recibosAntyAct:
				detalles = Detalle.objects.filter(idRecibo=factura.id)
				if detalles:
					# costo=0
					for detalle in detalles:
						costo = costo+detalle.valor
		fechacobrada = str(recibo.fecha_cobrada)
		dato={"reciboid":recibo.id,"reciboConsecutivo":recibo.numConsecutivo,\
			"fechacobrada":fechacobrada,"costo":costo}
		lista.append(dato)
	return lista

# INICIO METODO HACER INTERESES AUTOMATICAMENTE
# def InteresAuto:

# FIN INTERESES AUTOMATICAMENTE


# INICIO listarPagos
# listarpagos metodo para listar todos los pagos realizados de una unidad
class listarPagos(ListView):
	model = RecibosPagos
	template_name = "Pagos/RecibosPagos_list.html"

	def get_context_data(self, **kwargs):
		context = super(listarPagos, self).get_context_data(**kwargs)
		uid = self.request.user.id
		idpro = self.kwargs.get('id_propiedad',0)
		pkunidad= self.kwargs.get('pk',0)
		# realizamos la consulta para obtener los recibos pagos
		pagos= RecibosPagos.objects.filter(recibo__unidad = pkunidad, recibo__unidad__propiedad__idlegal=idpro)
		context['object_list']= pagos
		return context

# FIN listarPagos
# INICIO verPago
def verPago(request):
	if request.is_ajax() or request:
		# uid= request.user.id
 		idcomprobante = request.GET['idcomprobante']
 		pago = RecibosPagos.objects.filter(id = idcomprobante).\
 			values("no_comprobante","pagador","suma","enletras","concepto",\
 				"forma_pago","referencia1","referencia2","tipo")
 		temp = RecibosPagos.objects.filter(id = idcomprobante)
 		dia = temp[0].fecha_generacion.day
 		mes = temp[0].fecha_generacion.month
 		año = temp[0].fecha_generacion.year
 		recibo ="Consecutivo (#"+str(temp[0].recibo.numConsecutivo)+") "
 		recibo +=str(temp[0].recibo.fecha_cobrada)
 		respuesta=list(pago)
 		# agregamos al diccionario el dia, mes y año
 		respuesta[0]['dia']=dia
 		respuesta[0]['mes']=mes
 		respuesta[0]['anio']=año
 		respuesta[0]['recibo']=recibo

 		# respuesta.append(dia)
 		return HttpResponse( json.dumps(respuesta), content_type='application/json' )


	else:
 		return HttpResponse("Error! what are you doing noob?")

# FIN verPago



#INICIO crearcuotaextra
def CuotaextraCreate(request):
	if request.is_ajax():# or request:
		if request.method == 'POST':	#Para POST
			form = CuotaextraForm(request.POST)
			response_data = {}
			if form.is_valid(): # si el formulario es valido
				Cextra = form.save(commit=False)
				Cextra.estado = 1
				Cextra.save()
				# ya con el formulario guardado, creamos las cuotas para cada
				# unidad, para ello llamamos a todas las unidades de la propiedad
				propiedad = Cextra.propiedad
				unidades = Unidad.objects.filter(propiedad = propiedad.idlegal)
				cunidades = unidades.count() # cantidad de unidades
				tipocuota = Cextra.tipo_cuota
				cuotas = Cextra.cuotas
				valorc = Cextra.valor # valor de la cuota extra
				# si 0, significa que son iguales las cuotas
				if tipocuota == 0 or tipocuota == "0":
					valorcuota = int((valorc / cunidades)/ cuotas)
					for unidad in unidades:
						cuotafinal = CuotaExtraUnidad(idExtraordinaria=Cextra,
									unidad = unidad, valor = valorcuota,
									cont_cuota = 0)
						cuotafinal.save()
				# si 1, sgnifica que es por coeficientes
				else:
					presupuesto = unidades[0].propiedad.presupuesto_anual
					for unidad in unidades:
						valorcuota = ((valorc * unidad.coeficiente) / 100)/cuotas
						cuotafinal = CuotaExtraUnidad(idExtraordinaria=Cextra,
									unidad = unidad, valor = valorcuota,
									cont_cuota = 0)
						cuotafinal.save()
				response_data['success'] = 'guardado exitosamente'

			else:				# sino es valido mandamos los errores
				response_data['errors'] =form.errors
			return HttpResponse(
				json.dumps(response_data),
				content_type="application/json"
				)
		# else: # para metodo GET
	else:
		return HttpResponse(
			json.dumps({"Nada que ver": "Esto no sucederia"}),
			content_type="application/json"
			)
# FIN crearcuotaextra