from django.conf.urls import url

from apps.usuarios.views import index ,listar



urlpatterns = [

    url(r'^$', index), #mostrara el mensaje
    # url(r'^algo$', index), #otra forma, ejemplo adopcion/algo
    url(r'^listar$', listar, name = 'Solicitud_listar'),#listara los administradores
    # url(r'^solicitud/nuevo$', SolicitudCreate.as_view(), name = 'Solicitud_crear'),
    # url(r'^solicitud/editar/(?P<pk>\d+)$', SolicitudUpdate.as_view(), name = 'Solicitud_editar'),
    # url(r'^solicitud/eliminar/(?P<pk>\d+)$', SolicitudDelete.as_view(), name = 'Solicitud_eliminar'),

]
