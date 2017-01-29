from django.conf.urls import url

from apps.edificios.views import index, listarList, apartamentos, listar \
                               , PropiedadCreate, UnidadCreate, BancoCreate\
                               , BancoList, BancoEdit \
                               , PropiedadEdit \
                               , UnidadEdit \
                               , NotiVencidas, PersonaCreate\
                               , Buscador, Addpago \
                               , pruebas

from apps.pagos.views import ReciboList, DetalleFactura \
                            , FacturaCreate, probar, GenerardorGlobal\
                            , pruebagenerador \
                            ,DeudaUnidad, CarteraList\
                            ,NoticiaList,listarPagos, verPago\
                            ,CuotaextraCreate

urlpatterns = [

    url(r'^$', index), #mostrara el mensaje
    # url(r'^algo$', index), #otra forma, ejemplo adopcion/algo

    # url(r'^listar/$', listar, name = 'Solicitud_listar'),#listara los administradores
    url(r'^crear/$', PropiedadCreate.as_view(), name = 'Solicitud_crearpro'),#listara los administradores
    url(r'^listar/$', listarList.as_view(), name = 'Solicitud_listar'),#listara las propiedades
    url(r'^edit/(?P<pk>[A-Za-z0-9-_]+)$', PropiedadEdit.as_view(), name = 'Solicitud_updatePro'),#listara los administradores

    url(r'^listar/unidad/(?P<id_propiedad>[A-Za-z0-9-_]+)/crear/$', UnidadCreate.as_view(), name = 'Solicitud_crearuni'),#listara los administradores
    url(r'^bancos/crear$', BancoCreate.as_view(), name = 'Solicitud_crearBanco'),#listara los administradores
    url(r'^bancos/listar$', BancoList.as_view(), name = 'Solicitud_listarBanco'),#listara los administradores
    url(r'^bancos/edit/(?P<pk>\d+)$', BancoEdit.as_view(), name = 'Solicitud_updateBanco'),#listara los administradores


    # url(r'^solicitud/nuevo$', SolicitudCreate.as_view(), name = 'Solicitud_crear'),
    # url(r'^solicitud/editar/(?P<pk>\d+)$', SolicitudUpdate.as_view(), name = 'Solicitud_editar'),
    # url(r'^solicitud/eliminar/(?P<pk>\d+)$', SolicitudDelete.as_view(), name = 'Solicitud_eliminar'),
    # url(r'^apartamentos$', apartamentos, name = 'Solicitud_apartamentos'),#listara los administradores
    # url(r'^listar/(?P<id_propiedad>\w+)/$', apartamentos, name = 'Solicitud_apartamentos'),#listara los administradores
    # url(r'^unidades/$', apartamentos, name = 'Solicitud_apartamentos'),#listara los administradores
    url(r'^listar/unidades/(?P<id_propiedad>[A-Za-z0-9-_]+)/$', apartamentos, name = 'Solicitud_apartamentos'),#listara los apartamentos de una propiedad
    # agregar persona
    url(r'^listar/unidades/(?P<id_propiedad>[A-Za-z0-9-_]+)/addpersona$', PersonaCreate.as_view(), name = 'Solicitud_crearpersona'),#listara los apartamentos de una propiedad

    # editar unidad
    url(r'^listar/unidades/(?P<id_propiedad>[A-Za-z0-9-_]+)/(?P<pk>[A-Za-z0-9-_]+)/edit$', UnidadEdit.as_view(), name = 'Solicitud_updateUni'),#listara los administradores

# para pagos
    url(r'^listar/unidades/(?P<id_propiedad>[A-Za-z0-9-_]+)/(?P<pk>[A-Za-z0-9-_]+)/pagos$', ReciboList.as_view(), name = 'Solicitud_appagos'),#listara los administradores
# para listar los pagos realizados
    url(r'^listar/unidades/(?P<id_propiedad>[A-Za-z0-9-_]+)/(?P<pk>[A-Za-z0-9-_]+)/comprobantesdepago$', listarPagos.as_view(), name = 'Solicitud_comprobante'),#listara los administradores

    url(r'^listar/unidades/(?P<id_propiedad>[A-Za-z0-9-_]+)/(?P<pk>[A-Za-z0-9-_]+)/detallefactura/(?P<factura>[A-Za-z0-9-_]+)/$', DetalleFactura.as_view(), name = 'Solicitud_pagosdetalle'),#listara los administradores
    url(r'^listar/unidades/(?P<id_propiedad>[A-Za-z0-9-_]+)/(?P<pk>[A-Za-z0-9-_]+)/pagos/addFactura$', FacturaCreate.as_view(), name = 'Solicitud_addfactura'),#listara los administradores
    url(r'^listar/unidades/(?P<id_propiedad>[A-Za-z0-9-_]+)/cartera$', CarteraList.as_view(), name = 'Solicitud_Cartera'),#mostrara la cartera de la propiedad enviada
    # listar noticias
    url(r'^noticias/listar$', NoticiaList.as_view(), name = 'Solicitud_listarNoticias'),#listara los administradores
    # solo test y generador automatico de factura default=generador2
    url(r'^probar/$', NotiVencidas,name="probar"),
    url(r'^busqueda/$', Buscador,name="buscador"),
    url(r'^addpago/$', Addpago,name="Addpago"),
    url(r'^verpago/$', verPago,name="verpago"),
# para agregar una cuota extra
    url(r'^addcextra/$', CuotaextraCreate,name="Addcextra"),


    url(r'^pruebas/$', pruebas,name="prueba"),
    
    url(r'^generador/$', GenerardorGlobal,name="generar"),
    url(r'^generador2/$', pruebagenerador,name="generar2"),




    # url(r'^editar/(?P<pk>\d+)/$', MascotaUpdate.as_view() , name ='mascota_editar'),

]
