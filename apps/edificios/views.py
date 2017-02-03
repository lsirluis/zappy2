from django.shortcuts import render, reverse

import json
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import HttpResponse,HttpResponseRedirect ,HttpRequest
from django.core.urlresolvers import reverse_lazy
from django.utils.six.moves import zip_longest 
from django.utils.html import escape

from django.contrib import messages
import datetime 
from datetime import  date, time, timedelta
from django.utils import timezone 
from django.db.models import Q
from django.db.models import F


from django.views.generic import ListView, CreateView, UpdateView, DeleteView

from apps.edificios.models import Propiedad, Unidad, Persona, Banco
from apps.usuarios.models import Administrador
from apps.pagos.models import Recibo , Detalle, Noticia, DeNoticia \
							  ,Deuda , RecibosAuto ,RecibosPagos, RecibosyComprobante,Abono

from apps.edificios.forms import PropiedadForm,UnidadForm, BancoForm, PersonaForm,PagoForm
# from apps.pagos.forms import AddPagoForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

# inicio pruebas
from apps.pagos.views import listaReciboCosto

def Buscador(request):
 	if request.is_ajax() or request:
 		# usuario = [{'nombre':'Eduardo Ismael'},{'nombre':'javier'}]
 		uid= request.user.id
 		idunidad = request.GET['unidad']
 		propiedad = request.GET['propiedad']
 		if EsMiPropiedad(uid, propiedad):
 			if EsMiUnidad(uid, propiedad, idunidad):
 				unidadinfo = Unidad.objects.filter(id= idunidad, propiedad__administrador__idu=uid ).\
 					annotate(propi=F('propietario__nombre'),apellido=F('propietario__apellido')).\
 					values("torre","numero","propi","apellido")
		 		# dato={"DeudaTotal": 10000}
		 		respuesta=list(unidadinfo)
		 		# respuesta.append(dato)
		 		respuesta.append(listaReciboCosto(idunidad))
		 		respuesta.append(idunidad)
		 		# def listaReciboCosto(unidadid):

		 		# unidadinfo.append(dato)		
 				return HttpResponse( json.dumps(list(respuesta)), content_type='application/json' )
 			else:
 				return HttpResponse("Error no es la unidad")
 		else:
 			return HttpResponse("Error no es la propiedad")		
 		# usuario = Administrador.objects.filter(nombre1__startswith= request.GET['nombre'] ).values('nombre1','nombre2','apellido1', 'apellido2')
 		# return HttpResponse( json.dumps(list(usuario)), content_type='application/json' )
 	else:
 		return HttpResponse("Error! what are you doing noob?")

def pruebas(request):
	return render(request, "Propiedad/test.html","")


def Addpago(request): # agregar if es ajax
	if request.method == 'POST':
		# post_text = request.POST.get('the_post')
		response_data = {}
		# formu = AddPagoForm(request.POST)
		formu = PagoForm(request.POST)
		if formu.is_valid():
			# preguntamos primero la modalidad de pago, si es abono o pago total
			valor = int(request.POST.get('suma'))
			if request.POST.get('tipo') == "0": # si es o espago total
				idrecibo = request.POST.get('recibo')
				# procedemos a busca rle recibo en cuestion
				recibo = Recibo.objects.get(id = idrecibo)
	# ahora buscaremos los recibos anteriores que esten vencidos a este
	# y miraremos si el valor que se va a pagar el igual al total de la deuda
				idunidad= recibo.unidad
				Recendeuda = Recibo.objects.filter(Q(estado=0,unidad=idunidad\
									,fecha_generacion__lte=recibo.fecha_generacion)|Q(estado=2,unidad=idunidad\
									,fecha_generacion__lte=recibo.fecha_generacion))
	# ya teniendo todos los recibos incluyendo el rec en cuestion, procedemos
	# a sacar el costo total de la deuda conjunta de todos los recibos
				deuda=0
				for recibo in Recendeuda:
					deuda = deuda + Valordeudarecibo(recibo)					
				
				if valor >= deuda:
					comprobante = formu.save(commit=False)
					comprobante.save()
					for recibo in Recendeuda:
						recibo.estado = 1
						recibo.save()
						RyC = RecibosyComprobante(recibo= recibo, comprobante= comprobante, tipo=0)
						RyC.save()

					response_data['success'] = 'guardado exitosamente'
				else : 
					response_data['errors'] = {"recibo":" el valor pagado debe ser superior a la deuda, corrigalo o de lo contrario escoger la opcion de abono"}
			
			else: #PARA ABONO
			# buscamos los recibos en deuda de la unidad
				idunidad = request.POST.get('unidad')
				recibos = Recibo.objects.filter(Q(estado=0, unidad = idunidad) | Q(estado=2, unidad = idunidad) ).order_by('fecha_generacion')
			# guardamos el comprobante primero
				comprobante = formu.save(commit=False)
				comprobante.save()
			# procedemos a verificar si con la suma abonada se puede pagar 
			# el primer recibo
				for recibo in recibos:
					if valor >= Valordeudarecibo(recibo): # es un pago
						recibo.estado = 1
						recibo.save()
						RyC = RecibosyComprobante(recibo= recibo, comprobante= comprobante, tipo=0)
						RyC.save()
						valor = valor - Valordeudarecibo(recibo)
					else: # es un abono
						nuevovalor = Valordeudarecibo(recibo)
						recibo.estado = 2 # abonado
						recibo.save() 
						RyC = RecibosyComprobante(recibo= recibo, comprobante= comprobante, tipo=1)
						RyC.save()
						ReducirValorDetalles(recibo,valor)
						break
				response_data['success'] = 'Abonado exitosamente'

			# response_data['estado']+="valores"+ valor +" del " 
			# else:
			# response_data['success'] = 'guardado exitosamente'
		else:
			response_data['errors'] =formu.errors

		return HttpResponse(
			json.dumps(response_data),
			content_type="application/json"
		)
	else:
		return HttpResponse(
			json.dumps({"Nada que ver": "Esto no sucederia"}),
			content_type="application/json"
			)

# def deudas():

def Valordeudarecibo(recibo):
	deuda = 0
	detalles = Detalle.objects.filter(idRecibo = recibo.id)
	for detalle in detalles:
		deuda = deuda + detalle.valor
	return deuda

def ReducirValorDetalles(recibo,valor):
	detalles = Detalle.objects.filter(idRecibo = recibo.id).order_by('valor')
	suma = valor
	for detalle in detalles:
		if detalle.valor <= suma  :
			suma = suma - detalle.valor
			abono = Abono( detalle = detalle, \
							valor_inicial= detalle.valor,\
							valor_abonado= detalle.valor ,\
							valor_restante= 0)
			abono.save()
			detalle.valor = 0
			detalle.save()
		else:
			restante = detalle.valor - suma
			abono = Abono( detalle = detalle, \
							valor_inicial= detalle.valor,\
							valor_abonado= suma ,\
							valor_restante= restante)
			abono.save()
			detalle.valor = restante
			detalle.save()
			break


# Fin pruebas

# *********************************************************************

def NoticiasList(uid):
	# vamos a ver las noticias de el usuario enviado y no haigan sido vistas
	
	# detallenoticia = DeNoticia.objects.filter(idNoticia__administrador=uid, idNoticia__estado=0).order_by('idNoticia') 
	noticias = Noticia.objects.filter(administrador=uid, estado=0)
	dato = {}
	lista=[]
	if noticias:
		# teniendo las noticias buscare sus detalles
		for noticia in noticias:
			detalles = DeNoticia.objects.filter(idNoticia=noticia.id)
			dato={"propiedad":noticia.propiedad.nombre, 'unidades':detalles}
			lista.append(dato)
	# for noticias in noticia:
	return lista
# a continuacon el metodo que al pasar 7 dias pone las notificaciones en 
# no vistas pero no se mostraran ya en el apartado de noticias
def NotiVencidas(request):
	# buscamos las noticias que esten es 0 (no vistas)
	contador = 0
	formato1 = "%d-%m-%Y %H:%M:%S.%f"  
	noticias = Noticia.objects.filter(estado=0).order_by('fecha_generacion')
	for noticia in noticias:
		fecha = noticia.fecha_generacion

		fechatemp = "%s-%s-%s %s:%s:%s.%s" % (fecha.day, fecha.month, fecha.year, fecha.hour, fecha.minute, fecha.second, fecha.microsecond)
		Fechanot = datetime.datetime.strptime(str(fechatemp), formato1)
		ahora = datetime.datetime.now()
		if Fechanot < ahora:
			diferencia = ahora - Fechanot
			if diferencia.days >=1:
				Noti03(noticia)
				# return True
				contador=contador+1
			# else:
				# return False
				# return HttpResponse("No se actualizo")

			# return HttpResponse("Fecha de la noticia = %s </h1> y fecha actual = %s y resultado = %s" %(Fechanot, ahora, diferencia.days))
		# else: 
			# return HttpResponse("hay un error en la fecha")
			# return HttpResponse("Fecha de la noticia = %s </h1> y fecha actual = %s y resultado = %s" %(noticias[0].fecha_generacion, fecha, False))
			# return False
	if contador>0:
		return HttpResponse("se actualizo el estado a %s noticias" % contador)
	else:
		return HttpResponse("No se actualizo ninguna fecha")
# pasamos las noticias no vistas de 7 dias a estado no vista pero no visible
def Noti03(noticia):
	noticia.estado=2
	# noticia.fecha_generacion = noticia.fecha_generacion
	noticia.save()
	# a=""




# Create your views here.
def index(request):
	return HttpResponse("Hola esta es la pagina de edificios")
@login_required()
def listar(request):
	uid = request.user.id
	usuario = User.objects.raw('SELECT * FROM auth_User where id=%s',([uid]))[0]
	propiedad = Propiedad.objects.filter(administrador=usuario.identificacion)

	contexto = {'propiedades': propiedad,'messages':["hola"],'title':"nuevotitulo"}
	# return render(request, 'Propiedad/Propiedad_List.html',contexto)
	return render(request, 'Propiedad/MisPropiedades.html',contexto)

def usuarioId(id): 
	uid = id
	usuario = User.objects.raw('SELECT * FROM auth_User where id=%s',([uid]))[0]
	return usuario


class listarList(ListView):
	paginate_by =3
	model = Propiedad
	# queryset = Propiedad.objects.filter(administrador=usuario)
	template_name = 'Propiedad/MisPropiedades.html'

	# def get_queryset(self):
		# uid = self.request.user.id
		# usuario = User.objects.raw('SELECT * FROM auth_User where id=%s',([uid]))[0]
		# usuario = usuarioId(self.request.user.id)
		# contexto = Propiedad.objects.filter(administrador=usuario.identificacion)

	def get_context_data(self, **kwargs):
		context = super(listarList, self).get_context_data(**kwargs)
		# usuario = usuarioId(self.request.user.id)
		# context['object_list'] = Propiedad.objects.filter(administrador=usuario.identificacion)
		uid = self.request.user.id
		# context['object_list'] = Propiedad.objects.filter(administrador__idu = uid)
		p = Paginator( Propiedad.objects.filter(administrador__idu = uid), self.paginate_by)
		page = self.request.GET.get('page')
		try:
			context['object_list'] = p.page(page)
		except PageNotAnInteger:
        # If page is not an integer, deliver first page.
			context['object_list'] = p.page(1)
		except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
			context['object_list'] = p.page(p.num_pages)

		# context['object_list'] = p.page(context['page_obj'].number)
		context['title']="Mis Propiedades"
		context['breadurl']=[{'nombre':'Propiedades'}]
		# datetime.datetime.now()
		# context['fecha']= fechaActual()
		context['fecha']= timezone.now()
		# context['noticia']= NoticiasList(uid)

		

		return context
	# paginate_by = 1	
		# return contexto

@login_required()
def apartamentos(request,id_propiedad):
	# uid = request.user.id
	# usuario = User.objects.raw('SELECT * FROM auth_User where id=%s',([uid]))[0]

	# propiedades = Propiedad.objects.filter(administrador=usuario.identificacion)
	# apartamento = Unidad.objects.filter(propiedad_id=propiedades)
	# return HttpResponse(id_propiedad)
	# usuario=usuarioId(uid)
	uid = request.user.id
	url = {}
	apartamento=""
	nombre=""
	deudas={}
	apartamento2=""
	switch=False
	V =""
	# mensaje = {}
	# messages.add_message(request, messages.INFO, 'Hello world.')
	if id_propiedad != "TOTALUNIDADES":
		# a=2
		# apartamento=Unidad.objects.filter(propiedad__identificacion=id_propiedad,propiedad__administrador=usuario.identificacion)
		# apartamento=Unidad.objects.filter(propiedad=id_propiedad,propiedad__administrador=usuario.identificacion)
		#si existe la propiedad 
		if Propiedad.objects.filter(administrador__idu = uid, idlegal=id_propiedad):
			url = Propiedad.objects.filter(idlegal=id_propiedad)[0]
			titulo = "Unidades en "+url.nombre
			#procedemos a reliazar la busque si es que hay 
			busqueda= request.GET.get('qpropietario', '0-_no')
			if busqueda !='0-_no': # si hay una busqueda 
				if busqueda == '': # si la busqueda es vacia
					apartamento=Unidad.objects.filter(propiedad__administrador__idu=uid, propiedad=id_propiedad)
					# messages.add_message(request, messages.ERROR, 'Lo sentimos, No hay propietario a buscar, escribalo en el campo')
				else: # si hay un valor a buscar
					apartamento= QunidadPropietario(id_propiedad,uid,busqueda)
					V = busqueda
			else: # conducto regular, es decir si no hay una busqueda
				apartamento=Unidad.objects.filter(propiedad__administrador__idu=uid, propiedad=id_propiedad).order_by('torre','numero')
			nombre=url.nombre
			if apartamento :
				titulo = "Unidades en "+url.nombre
				deudas=EnDeudaApartamentos((apartamento))
				apartamento2 = zip_longest(apartamento,deudas,"")
				apartamento2 = list(apartamento2)
			else:
			# titulo = "no hay unidades"
				# si hay una busqueda, pero sin resultados
				if busqueda !='0-_no':
					messages.add_message(request, messages.ERROR, 'Lo sentimos, no hubo ningun resultado para su busqueda')
				else:
					messages.add_message(request, messages.ERROR, 'No tiene ningun Apartamento en esta propiedad')

		else:
			titulo = "No Existe esta propiedad"
			nombre = titulo
			messages.add_message(request, messages.ERROR, 'Lo sentimos, está Propiedad no esta registrada')


		

			# messages.warning(request, 'Your account expires in three days.')
		# apartamento = Unidad.objects.raw('SELECT * FROM auth_User, edificios_propiedad, edificios_unidad \
									  # WHERE auth_User.id=%s\
									  # and auth_User.identificacion = edificios_propiedad.administrador_id \
									  # and edificios_propiedad.identificacion = edificios_unidad.propiedad_id and edificios_unidad.propiedad_id = %s',[uid,id_propiedad])
	else:
		url['Imagen']= "/IMG/Propiedad/default_building_zappy.jpg"
		titulo = "Todas mis Unidades"
		apartamento=Unidad.objects.filter(propiedad__administrador__idu=uid)
		# apartamento = Unidad.objects.filter(propiedad__administrador=usuario.identificacion).order_by("propiedad__nombre","torre","numero")
		# apartamento = Unidad.objects.raw('SELECT * FROM auth_User, edificios_propiedad, edificios_unidad \
									  # WHERE auth_User.id=%s \
									  # and auth_User.identificacion = edificios_propiedad.administrador_id \
									  # and edificios_propiedad.identificacion = edificios_unidad.propiedad_id',[uid])
	# return HttpResponse(apartamento)
	contexto = {'apartamentos': apartamento,'title':titulo,'DatosPropiedad':url}
	
	if V :
		contexto['busqueda'] = V
	if url:
		contexto['breadurl']=[{'nombre':'Propiedades','url':"Propiedad:Solicitud_listar"},\
							 {'nombre':nombre,'url':"Propiedad:Solicitud_apartamentos",'arg':id_propiedad}]	
		
	if "Unidades en " in titulo :
		contexto['deuda']=deudas
		contexto['apartamento2']=apartamento2
	return render(request, 'Propiedad/MisApartamentos.html',contexto)

def EnDeudaApartamentos(apartamentos):
	lista=[]
	for apartamento in apartamentos:
		recibos = Recibo.objects.filter(Q(unidad=apartamento.id,estado=0)| Q(unidad=apartamento.id,estado=2))
		if recibos or apartamento.valor_mora>0 :
			lista.append(True)
		else:
			lista.append(False)
		# lista.append(apartamento.id)
	# al final retorno la lista del estado de deuda (si, no), de apartamentos
	return lista

def QunidadPropietario(propiedad, uid, qpropietario):
	# primero contaremos el numero de palabras
	ListaPalabras = qpropietario.split()
	CantidadPalabras = len(ListaPalabras)
	# teniendo las palabras y la cantidad, procedemos
	# si hay una sola palabra, buscara en los nombres y en los apellidos
	apartamento = False
	if CantidadPalabras == 1:
		apartamento=Unidad.objects.filter(Q(propiedad__administrador__idu=uid, \
										  propiedad=propiedad, propietario__nombre=qpropietario)|\
										 Q(propiedad__administrador__idu=uid, \
										  propiedad=propiedad,propietario__apellido=qpropietario))
	elif CantidadPalabras == 2:
		apartamento=Unidad.objects.filter(Q(propiedad__administrador__idu=uid, \
										  propiedad=propiedad, propietario__nombre=qpropietario)|\
										 Q(propiedad__administrador__idu=uid, \
										  propiedad=propiedad,propietario__apellido=qpropietario)|\

										 Q(propiedad__administrador__idu=uid, \
										  propiedad=propiedad, propietario__nombre=ListaPalabras[0])|\
										 Q(propiedad__administrador__idu=uid, \
										  propiedad=propiedad,propietario__apellido=ListaPalabras[1]))
	return apartamento


# vista para crear una nueva propiedad
class PropiedadCreate(CreateView):
	model = Propiedad
	form_class = PropiedadForm
	template_name = 'Propiedad/Propiedad_form.html'
	success_url = reverse_lazy('Propiedad:Solicitud_listar')
	def get_context_data(self, **kwargs):
		context = super(PropiedadCreate, self).get_context_data(**kwargs)
		context['title']= "Agregar Nueva Propiedad"
		return context
	#metodo post, aqui agregaremos el administrador 
	def post(self, request, *args, **kwargs):
		self.object = self.get_object
		# quien es el administrador al que se le guardara? pues este:
		uid = request.user.id
		admin = Administrador.objects.get(idu=uid)
		form = self.form_class(request.POST, request.FILES)
		if form.is_valid() :
			solicitud = form.save(commit=False)
			solicitud.administrador = admin
			solicitud.save()		
			# form.administrador=1
			# form.save()			
			return HttpResponseRedirect(self.get_success_url())
		else:
			return self.render_to_response(self.get_context_data(form=form))	

class PropiedadEdit(UpdateView):
	model = Propiedad
	form_class = PropiedadForm
	template_name = 'Propiedad/Propiedad_form.html'
	success_url = reverse_lazy('Propiedad:Solicitud_listar')
	# def get_initial(self):
	# 	self.initial.update({ 'requests': self.request})
	# 	return self.initial
	# filtraremos los datos para que no se pueda editar un banco que no nos pertenezca
	def get_context_data(self, **kwargs):
		context = super(PropiedadEdit, self).get_context_data(**kwargs)
		uid = self.request.user.id
		pk = self.kwargs.get('pk',0)
		if Propiedad.objects.filter(idlegal=pk, administrador=uid):
			return context
		else:
			messages.add_message(self.request, messages.ERROR, 'Lo sentimos, esta Propiedad no está registrada')
			# context = ""
			context['title']="Propiedad no registrada"
			return context


class UnidadCreate(CreateView):
	model = Unidad
	form_class = UnidadForm
	def get_success_url(self):
		idpro = self.kwargs.get('id_propiedad',0)
		return reverse_lazy('Propiedad:Solicitud_apartamentos',args=[idpro])

	def get_initial(self):
		self.propiedad = self.kwargs.get('id_propiedad',0)
		self.initial.update({ 'request': self.request,'propiedad':self.propiedad})
		return self.initial
	def get_context_data(self, **kwargs):
		context = super(UnidadCreate, self).get_context_data(**kwargs)
		# usuario = usuarioId(self.request.user.id)
		# context['object_list'] = Propiedad.objects.filter(administrador=usuario.identificacion)
		uid = self.request.user.id
		self.propiedad = self.kwargs.get('id_propiedad',0)
		# qs = Propiedad.objects.filter(administrador__idu = uid, idlegal=propiedad)
		if(Propiedad.objects.filter(administrador__idu = uid, idlegal=self.propiedad)):
			qs = Propiedad.objects.filter(administrador__idu = uid, idlegal=self.propiedad)[0]
		else:
			qs=""
			messages.add_message(self.request, messages.ERROR, 'Lo sentimos, está Propiedad no esta registrada')

		context['object_list'] = qs
		context['title'] = "Crear Unidad en - "+qs.nombre
		# para popup
		try:
			popup = int(self.request.GET.get('_popup', '0'))
			context['is_popup']= popup
		except Exception as e:
			context['is_popup']= 0

		return context


	template_name = 'Propiedad/Unidad_form.html'
	# success_url = reverse_lazy('Propiedad:Solicitud_listar')

class UnidadEdit(UpdateView):
	model = Unidad
	form_class = UnidadForm
	template_name = 'Propiedad/Unidad_form.html'
	# success_url = reverse_lazy('Propiedad:Solicitud_listar')
	# idpro=self.kwargs.get('id_propiedad',0)
	# success_url = reverse_lazy('Propiedad:Solicitud_apartamentos',args=[idpro])
	def get_success_url(self):
		idpro = self.kwargs.get('id_propiedad',0)
		return reverse_lazy('Propiedad:Solicitud_apartamentos',args=[idpro])
	def get_initial(self):
		self.propiedad = self.kwargs.get('id_propiedad',0)
		self.initial.update({ 'request': self.request,'propiedad':self.propiedad})
		return self.initial
	def get_context_data(self, **kwargs):
		context = super(UnidadEdit, self).get_context_data(**kwargs)
		uid = self.request.user.id
		pkunidad = self.kwargs.get('pk',0)
		idpro = self.kwargs.get('id_propiedad',0)
		success_url = reverse_lazy('Propiedad:Solicitud_apartamentos',args=[idpro])
		if EsMiPropiedad(uid, idpro):
			if EsMiUnidad(uid, idpro, pkunidad):
		# if Unidad.objects.filter(propiedad__idlegal=idpro,id=pkunidad, propiedad__administrador=uid):
				context['title']="Editar unidad"
				context['object_list']= Propiedad.objects.filter(administrador__idu = uid, idlegal=idpro)[0]

				return context

			else:
				messages.add_message(self.request, messages.ERROR, 'Lo sentimos, esta Unidad no está registrada')
				context = ""
				context['title']="Unidad no registrada"
				context['form']=""
				# return context
		else:
			messages.add_message(self.request, messages.ERROR, 'Lo sentimos, esta Propiedad no está registrada')
			# context = ""
			context['title']="Propiedad no registrada"
			context['form']=""
		return context
	# def post(self, request, *args, **kwargs):
	# 	self.object = self.get_object
	# 	# quien es el administrador al que se le guardara? pues este:
	# 	# uid = request.user.id
	# 	idpro = self.kwargs.get('id_propiedad',0)
	# 	# admin = Administrador.objects.get(idu=uid)
	# 	# propiedad = Propiedad.objects.get(idlegal=idpro, administrador= uid)
	# 	kwargs = {'initial':{ 'request': self.request, 'propiedad':idpro}}
	# 	form = self.form_class(request.POST,**kwargs)
 
	# 	if form.is_valid() :
	# 		form.save()
	# 		self.success_url = reverse_lazy('Propiedad:Solicitud_apartamentos',args=[idpro])
	# 		return HttpResponseRedirect(self.get_success_url())
	# 	else:
	# 		return self.render_to_response(self.get_context_data(form=form))	


# reverse('arch-summary', args=[1945])
class BancoCreate(CreateView):
	model = Banco
	form_class = BancoForm
	template_name = 'Propiedad/Banco_form.html'
	success_url = reverse_lazy('Propiedad:Solicitud_listarBanco')

	def get_initial(self):
		self.initial.update({ 'requests': self.request})
		return self.initial

	def get_context_data(self, **kwargs):
		context = super(BancoCreate, self).get_context_data(**kwargs)
		uid = self.request.user.id
		context['administrador'] = uid
		context['title'] = "Crear Banco "
		return context


	# def post(self, request, *args, **kwargs):
	# 	self.object = self.get_object
	# 	# quien es el administrador al que se le guardara? pues este:
	# 	# initial.update({ 'request': self.request})
	# 	# return self.initial
	# 	# initial= self.initial
	# 	# initial.update({ 'requests': self.request})
	# 	kwargs.update({'initial':{'requests': self.request}})
	# 	uid = request.user.id
	# 	admin = Administrador.objects.get(idu=uid)
	# 	form['initial']='h'

	# 	if form.is_valid("hola") :
	# 		solicitud = form.save(commit=False)
	# 		solicitud.administrador = admin
	# 		solicitud.save()		
	# 		# form.administrador=1
	# 		# form.save()			
	# 		return HttpResponseRedirect(self.get_success_url())
	# 	else:
	# 		return self.render_to_response(self.get_context_data(form=form))	


class BancoList(ListView):
	model = Banco
	template_name = 'Propiedad/MisBancos.html'	
	def get_context_data(self, **kwargs):
		context = super(BancoList, self).get_context_data(**kwargs)
		uid = self.request.user.id
		context['object_list']= Banco.objects.filter(administrador = uid)
		context['title']= "Mis Bancos"
		return context
class BancoEdit(UpdateView):
	model = Banco
	form_class = BancoForm
	template_name = 'Propiedad/Banco_form.html'
	success_url = reverse_lazy('Propiedad:Solicitud_listarBanco')
	def get_initial(self):
		self.initial.update({ 'requests': self.request})
		return self.initial
	# filtraremos los datos para que no se pueda editar un banco que no nos pertenezca
	def get_context_data(self, **kwargs):
		context = super(BancoEdit, self).get_context_data(**kwargs)
		uid = self.request.user.id
		pk = self.kwargs.get('pk',0)
		if Banco.objects.filter(id=pk, administrador=uid):
			return context
		else:
			messages.add_message(self.request, messages.ERROR, 'Lo sentimos, este Banco no está registrado')
			# context = ""
			context['title']="Banco no registrado"
			return context

# INICIO CREAR PERSONA
class PersonaCreate(CreateView):
	model = Persona
	form_class = PersonaForm
	template_name = 'Propiedad/Persona_form.html'
	success_url = reverse_lazy('Propiedad:Solicitud_listar')
	def get_initial(self):
		propiedad = self.kwargs.get('id_propiedad',0)
		self.initial.update({ 'requests': self.request, 'propiedad':propiedad})
		return self.initial
	def get_context_data(self, **kwargs):
		context = super(PersonaCreate, self).get_context_data(**kwargs)
		uid = self.request.user.id
		propiedad = self.kwargs.get('id_propiedad',0)
		if EsMiPropiedad(uid,propiedad):
			context['title']= "Agregar Nueva Persona | Zappy"
		else:
			messages.add_message(self.request, messages.ERROR, "Esta propiedad no existe")
			context['title']= "Lo sentimos, esta propiedad no existe"
		try:
			popup = int(self.request.GET.get('_popup', '0'))
			context['is_popup']= popup
		except Exception as e:
			context['is_popup']= 0
		return context
	#metodo post, aqui agregaremos el administrador y propiedad
	def post(self, request, *args, **kwargs):
		self.object = self.get_object
		# quien es el administrador al que se le guardara? pues este:
		uid = request.user.id
		idpro = self.kwargs.get('id_propiedad',0)
		admin = Administrador.objects.get(idu=uid)
		propiedad = Propiedad.objects.get(idlegal=idpro, administrador= uid)
		kwargs = {'initial':{ 'requests': self.request, 'propiedad':idpro}}
		form = self.form_class(request.POST,**kwargs)
 
		if form.is_valid() :
		# if 2+2 == 4:	
			solicitud = form.save(commit=False)
			solicitud.administrador = admin
			solicitud.propiedad = propiedad
			solicitud.save()
			newObject = form.save()		
			# form.administrador=1
			# form.save()		
			if self.request.GET.get('_popup','0'):
				return HttpResponse('<script type="text/javascript">opener.dismissAddAnotherPopup(window, "%s", "%s");</script>' % \
						(escape(newObject._get_pk_val()), escape(newObject)))



			# if self.request.GET.get('_popups', '0'):
				# return HttpResponse('<script language="javascript" >\
					# function activ(){\
										# opener.document.getElementById("id_prueba").innerHTML = "A new window has been opened.";alert("activvado") ;}</script> <body> <button onclick="activ()">proba</button></body> ')
										# opener.document.forms["unidad_form"].prueba.value = "Hola";</script>')
			self.success_url = reverse_lazy('Propiedad:Solicitud_apartamentos',args=[idpro])
			return HttpResponseRedirect(self.get_success_url())
		else:
			return self.render_to_response(self.get_context_data(form=form))	

	
# FIN CREAR PERSONA









def EsMiPropiedad(idadmin, idpro):
	if Propiedad.objects.filter(administrador=idadmin, idlegal= idpro) :
		return True
	return False;

def EsMiUnidad(idadmin, idpro, idunidad):
	if Unidad.objects.filter(propiedad=idpro,id= idunidad, propiedad__administrador= idadmin) :
		return True
	return False;

def fechaActual():
	fecha = datetime.datetime.now()
	ahora = "%s/%s/%s" % (fecha.day, fecha.month, fecha.year)
	return ahora

