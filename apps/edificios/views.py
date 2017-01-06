from django.shortcuts import render, reverse

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


from django.views.generic import ListView, CreateView, UpdateView, DeleteView

from apps.edificios.models import Propiedad, Unidad, Persona, Banco
from apps.usuarios.models import Administrador
from apps.pagos.models import Recibo , Detalle, Noticia, DeNoticia \
							  ,Deuda , RecibosAuto

from apps.edificios.forms import PropiedadForm,UnidadForm, BancoForm, PersonaForm

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

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
	paginate_by =9
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
			apartamento=Unidad.objects.filter(propiedad__administrador__idu=uid, propiedad=id_propiedad)
			if apartamento :
				titulo = "Unidades en "+url.nombre
				nombre=url.nombre
				deudas=EnDeudaApartamentos((apartamento))
				apartamento2 = zip_longest(apartamento,deudas,"")
				apartamento2 = list(apartamento2)
			else:
			# titulo = "no hay unidades"
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
	if "Unidades en " in titulo :
		contexto['breadurl']=[{'nombre':'Propiedades','url':"Propiedad:Solicitud_listar"},\
								 {'nombre':nombre,'url':"Propiedad:Solicitud_apartamentos",'arg':id_propiedad}]	
		contexto['deuda']=deudas
		contexto['apartamento2']=apartamento2
	return render(request, 'Propiedad/MisApartamentos.html',contexto)

def EnDeudaApartamentos(apartamentos):
	lista=[]
	for apartamento in apartamentos:
		recibos = Recibo.objects.filter(unidad=apartamento.id,estado=0)
		if recibos or apartamento.valor_mora>0 :
			lista.append(True)
		else:
			lista.append(False)
		# lista.append(apartamento.id)
	# al final retorno la lista del estado de deuda (si, no), de apartamentos
	return lista


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
		form = self.form_class(request.POST)
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
	success_url = reverse_lazy('Propiedad:Solicitud_listar')

class UnidadEdit(UpdateView):
	model = Unidad
	form_class = UnidadForm
	template_name = 'Propiedad/Unidad_form.html'
	success_url = reverse_lazy('Propiedad:Solicitud_listar')
	def get_initial(self):
		self.initial.update({ 'request': self.request})
		return self.initial
	def get_context_data(self, **kwargs):
		context = super(UnidadEdit, self).get_context_data(**kwargs)
		uid = self.request.user.id
		pkunidad = self.kwargs.get('pk',0)
		idpro = self.kwargs.get('id_propiedad',0)
		if EsMiPropiedad(uid, idpro):
			if EsMiUnidad(uid, idpro, pkunidad):
		# if Unidad.objects.filter(propiedad__idlegal=idpro,id=pkunidad, propiedad__administrador=uid):
				context['title']="Editar unidad"
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

