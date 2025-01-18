from django.contrib import admin
from .models import (ClienteRegistrado, Administrador, Ropa, Servicio, Pedido, DetallePedido, Ruta, OrdenEntrega, Transporte, Repartidor, Sucursal, Pago, Tarjeta, Puntuacion)
from .forms import *

class ClienteRegistradoAdmin(admin.ModelAdmin):
    form = ClienteForm
    list_display = ('user', 'dir_cliente', 'colonia_cliente', 'codigo_postal', 'tel_cliente', 'fecha_nacimiento')
    search_fields = ('user__username', 'dir_cliente', 'colonia_cliente')
    list_filter = ('colonia_cliente', 'codigo_postal')

class AdministradorAdmin(admin.ModelAdmin):
    list_display = ('user', 'dir_admin', 'colonia_admin', 'tel_admin', 'especialidad')
    search_fields = ('user__username', 'dir_admin')
    list_filter = ('colonia_admin',)

class RopaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'precio')
    search_fields = ('nombre',)

class ServicioAdmin(admin.ModelAdmin):
    list_display = ('tipo', 'descripcion', 'precio_adicional')
    search_fields = ('tipo',)

class DetallePedidoInline(admin.TabularInline):
    model = DetallePedido
    extra = 1

class PedidoAdmin(admin.ModelAdmin):
    form = PedidoForm
    list_display = ('id', 'estado', 'fecha_pedido', 'cliente', 'administrador')
    search_fields = ('cliente__user__username', 'administrador__user__username')
    list_filter = ('estado',)
    inlines = [DetallePedidoInline]


class RutaAdmin(admin.ModelAdmin):
    list_display = ('nom_ruta', 'dir_origen', 'col_origen', 'sucursal', 'cliente', 'admin')
    search_fields = ('nom_ruta', 'cliente__user__username')
    list_filter = ('col_origen',)

class OrdenEntregaAdmin(admin.ModelAdmin):
    list_display = ('nom_ordenentrega', 'fecha_actual', 'hora', 'cliente', 'ruta_orden', 'sucursal', 'repartidor', 'pedidos', 'admin')
    search_fields = ('nom_ordenentrega', 'cliente__user__username')
    list_filter = ('sucursal',)

class TransporteAdmin(admin.ModelAdmin):
    list_display = ('modelo_trans', 'marca_trans', 'año_trans', 'color_trans', 'repartidor', 'sucursal')
    search_fields = ('modelo_trans', 'marca_trans')
    list_filter = ('sucursal',)

class RepartidorAdmin(admin.ModelAdmin):
    form = RepartidorForm
    list_display = ('user', 'dir_repar', 'colonia_repar', 'tel_repar', 'licencia_conducir')
    search_fields = ('user__username',)

class SucursalAdmin(admin.ModelAdmin):
    list_display = ('nom_sucursal', 'calle_sucursal', 'col_sucursal')
    search_fields = ('nom_sucursal',)

class PagoAdmin(admin.ModelAdmin):
    form = PagoForm
    list_display = ('cliente', 'pedido', 'fecha_pago', 'monto', 'metodo_pago')
    search_fields = ('cliente__user__username', 'pedido__id')
    list_filter = ('metodo_pago',)

class TarjetaAdmin(admin.ModelAdmin):
    form = TarjetaForm
    list_display = ('nom_titular', 'num_tarjeta', 'fecha_ven_tarjeta', 'nip_tarjeta')
    search_fields = ('nom_titular', 'num_tarjeta')

class PuntuacionAdmin(admin.ModelAdmin):
    list_display = ('no_estrellas', 'comentarios', 'cliente', 'tipo_servicio', 'administrador')
    search_fields = ('cliente__user__username',)

# Registrar los modelos en el panel de administración de Django
admin.site.register(ClienteRegistrado, ClienteRegistradoAdmin)
admin.site.register(Administrador, AdministradorAdmin)
admin.site.register(Ropa, RopaAdmin)
admin.site.register(Servicio, ServicioAdmin)
admin.site.register(Pedido, PedidoAdmin)
admin.site.register(DetallePedido)
admin.site.register(Ruta, RutaAdmin)
admin.site.register(OrdenEntrega, OrdenEntregaAdmin)
admin.site.register(Transporte, TransporteAdmin)
admin.site.register(Repartidor, RepartidorAdmin)
admin.site.register(Sucursal, SucursalAdmin)
admin.site.register(Pago, PagoAdmin)
admin.site.register(Tarjeta, TarjetaAdmin)
admin.site.register(Puntuacion, PuntuacionAdmin)
