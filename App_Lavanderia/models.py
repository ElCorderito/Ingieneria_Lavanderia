from django.db import models
from django.core.validators import RegexValidator
from django.contrib.auth.models import User
import datetime
from django.db.models.signals import post_save
from django.dispatch import receiver

class Tarjeta(models.Model):
    nom_titular = models.CharField(max_length=100)
    num_tarjeta = models.CharField(max_length=16)
    fecha_ven_tarjeta = models.DateField()
    nip_tarjeta = models.CharField(max_length=4)

    def __str__(self):
        return self.nom_titular


class ClienteRegistrado(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    dir_cliente = models.CharField(max_length=200)
    colonia_cliente = models.CharField(max_length=100)
    codigo_postal = models.CharField(max_length=10)
    tel_cliente = models.CharField(max_length=15)
    fecha_nacimiento = models.DateField()
    tarjeta_credito = models.OneToOneField(Tarjeta, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return str(self.user) if self.user else "Cliente Desconocido"


class Administrador(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    dir_admin = models.CharField(max_length=200)
    colonia_admin = models.CharField(max_length=100)
    codigo_postal = models.CharField(max_length=10)
    tel_admin = models.CharField(max_length=15)
    direccion_trabajo = models.CharField(max_length=200, blank=True, null=True)
    especialidad = models.CharField(max_length=100, blank=True, null=True)
    foto = models.ImageField(upload_to='admin_fotos/', blank=True, null=True)

    def __str__(self):
        return str(self.user) if self.user else "Administrador Desconocido"


class Ropa(models.Model):
    nombre = models.CharField(max_length=100)
    precio = models.DecimalField(max_digits=6, decimal_places=2)

    def __str__(self):
        return f'{self.nombre} - ${self.precio}'


class Servicio(models.Model):
    tipo = models.CharField(max_length=100)
    descripcion = models.TextField()
    precio_adicional = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)

    def __str__(self):
        return f'{self.tipo}'


class EstadoPedido(models.TextChoices):
    CREANDO = 'CR', 'Creando'
    EN_ESPERA = 'EN', 'En espera'
    ACEPTADO = 'AC', 'Aceptado'
    TERMINADO = 'TE', 'Terminado'
    RECHAZADO = 'RE', 'Rechazado'


class Pedido(models.Model):
    estado = models.CharField(max_length=2, choices=EstadoPedido.choices, default=EstadoPedido.CREANDO,)
    fecha_pedido = models.DateTimeField(auto_now_add=True)
    cliente = models.ForeignKey('ClienteRegistrado', on_delete=models.CASCADE)
    administrador = models.ForeignKey('Administrador', on_delete=models.SET_NULL, null=True)
    servicio = models.ForeignKey('Servicio', on_delete=models.SET_NULL, null=True, related_name='servicios_pedido')
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)  # Primero guarda el objeto para asegurar que tiene una clave primaria
        self.total = self.calcular_total()  # Ahora puedes calcular el total
        super().save(update_fields=['total'])  # Guarda nuevamente para actualizar el campo total

    def calcular_total(self):
        total = 0
        for detalle in self.detalles.all():
            total += detalle.cantidad * detalle.ropa.precio
        if self.servicio:
            total += self.servicio.precio_adicional
        return total


    def __str__(self):
        return f'Pedido {self.id}'


class DetallePedido(models.Model):
    pedido = models.ForeignKey(Pedido, related_name='detalles', on_delete=models.CASCADE)
    ropa = models.ForeignKey(Ropa, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField()

    def __str__(self):
        return f'{self.ropa.nombre} - {self.cantidad} unidades'


@receiver(post_save, sender=DetallePedido)
def update_pedido_total(sender, instance, **kwargs):
    if instance.pedido:
        instance.pedido.save()


class Ruta(models.Model):
    nom_ruta = models.CharField(max_length=100)
    dir_origen = models.CharField(max_length=200)
    col_origen = models.CharField(max_length=100)
    postal_origen = models.CharField(max_length=10)
    sucursal = models.ForeignKey('Sucursal', on_delete=models.CASCADE)
    cliente = models.ForeignKey(ClienteRegistrado, on_delete=models.CASCADE)
    lavado_ruta = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name='rutas')
    repartidor = models.ForeignKey('Repartidor', on_delete=models.CASCADE)
    orden_entrega = models.ForeignKey('OrdenEntrega', on_delete=models.CASCADE)
    admin = models.ForeignKey('Administrador', on_delete=models.CASCADE)

    def __str__(self):
        return self.nom_ruta


class OrdenEntrega(models.Model):
    nom_ordenentrega = models.CharField(max_length=100)
    fecha_actual = models.DateField()
    hora = models.TimeField()
    cliente = models.ForeignKey(ClienteRegistrado, on_delete=models.CASCADE)
    ruta_orden = models.ForeignKey(Ruta, on_delete=models.CASCADE, related_name='ordenes_entrega')
    sucursal = models.ForeignKey('Sucursal', on_delete=models.CASCADE)
    repartidor = models.ForeignKey('Repartidor', on_delete=models.CASCADE)
    pedidos = models.ForeignKey('Pedido', on_delete=models.CASCADE)
    admin = models.ForeignKey('Administrador', on_delete=models.CASCADE)

    def __str__(self):
        return self.nom_ordenentrega


class Puntuacion(models.Model):
    no_estrellas = models.IntegerField()
    comentarios = models.CharField(max_length=200)
    mejoras = models.CharField(max_length=100)
    cliente = models.ForeignKey(ClienteRegistrado, on_delete=models.CASCADE)
    tipo_servicio = models.ForeignKey(Pedido, on_delete=models.CASCADE)
    administrador = models.ForeignKey(Administrador, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.cliente} - {self.tipo_servicio} - {self.no_estrellas}"


class Transporte(models.Model):
    modelo_trans = models.CharField(max_length=100)
    marca_trans = models.CharField(max_length=100)
    año_trans = models.IntegerField()
    color_trans = models.CharField(max_length=100)
    repartidor = models.ForeignKey('Repartidor', on_delete=models.CASCADE)
    sucursal = models.ForeignKey('Sucursal', on_delete=models.CASCADE)
    pedidos = models.ForeignKey(Pedido, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.modelo_trans} - {self.marca_trans}"


class Repartidor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    dir_repar = models.CharField(max_length=200)
    colonia_repar = models.CharField(max_length=100)
    tel_repar = models.CharField(max_length=15)
    licencia_conducir = models.CharField(max_length=20)
    foto = models.ImageField(upload_to='repartidor_fotos/', blank=True, null=True)

    def __str__(self):
        return str(self.user)


class Sucursal(models.Model):
    nom_sucursal = models.CharField(max_length=100)
    calle_sucursal = models.CharField(max_length=200)
    col_sucursal = models.CharField(max_length=100)
    no_exterior_sucursal = models.CharField(max_length=10)
    no_interior_sucursal = models.CharField(max_length=10)

    def __str__(self):
        return self.nom_sucursal


class Pago(models.Model):
    cliente = models.ForeignKey(ClienteRegistrado, on_delete=models.CASCADE)
    pedido = models.OneToOneField(Pedido, on_delete=models.CASCADE, related_name='pago_detalle', null=True)
    fecha_pago = models.DateTimeField(default=datetime.datetime.now)
    monto = models.DecimalField(max_digits=8, decimal_places=2, default=0.0)
    metodo_pago = models.CharField(max_length=50, default='Tarjeta de Crédito')

    def __str__(self):
        return f"Pago de {self.monto} por {self.cliente.user.username} para el pedido {self.pedido.id if self.pedido else 'No asignado'}"
    
