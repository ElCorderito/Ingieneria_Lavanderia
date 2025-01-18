from django.shortcuts import render, redirect, get_object_or_404
from datetime import datetime
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.contrib import messages
from .forms import *
from .models import *
from django.db import transaction
from django.forms import formset_factory
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.forms import inlineformset_factory
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse


def landing(request):
    return render(request, 'landing_page.html')


def index(request):
    return render(request, 'index.html')


def index_cliente(request):
    return render(request, 'index_cliente.html')


def ver_usuarios(request):
    clientes = ClienteRegistrado.objects.all()
    repartidores = Repartidor.objects.all()
    admin = Administrador.objects.all()
    usuarios = User.objects.all()
    return render(request, 'ver_clientes.html', {'clientes': clientes, 'usuarios': usuarios, 'repartidores': repartidores, 'admin': admin})


def crear_usuario(request):
    if request.method == 'POST':
        form = UsuarioForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])  # Asegúrate de establecer la contraseña correctamente
            user.save()
            return redirect('ver_usuarios')  # Redirige a la vista de ver clientes
    else:
        form = UsuarioForm()
    return render(request, 'crear_usuario.html', {'form': form})


def crear_cliente(request):
    if request.method == 'POST':
        form = ClienteForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('ver_usuarios')  # Redirige a la vista de ver clientes
    else:
        form = ClienteForm()
    return render(request, 'crear_cliente.html', {'form': form})


def crear_repartidor(request):
    if request.method == 'POST':
        form = RepartidorForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('ver_usuarios')  # Redirige a la vista de ver usuarios
    else:
        form = RepartidorForm()
    return render(request, 'crear_repartidor.html', {'form': form})


def actualizar_repartidor(request, repartidor_id):
    repartidor = get_object_or_404(Repartidor, pk=repartidor_id)
    if request.method == 'POST':
        form = RepartidorForm(request.POST, instance=repartidor)
        if form.is_valid():
            form.save()
            return redirect('ver_usuario', repartidor_id=repartidor_id)
    else:
        form = RepartidorForm(instance=repartidor)
    return render(request, 'actualizar_repartidor.html', {'form': form, 'repartidor': repartidor})


def cliente_creado(request):
    return render(request, 'cliente_creado.html')


def actualizar_cliente(request, cliente_id):
    cliente = get_object_or_404(ClienteRegistrado, pk=cliente_id)
    if request.method == 'POST':
        form = ClienteForm(request.POST, instance=cliente)
        if form.is_valid():
            form.save()
            return redirect('ver_usuario', cliente_id=cliente_id)
    else:
        form = ClienteForm(instance=cliente)
    return render(request, 'actualizar_cliente.html', {'form': form, 'cliente': cliente})


def listar_pedidos(request):
    pedidos = Pedido.objects.filter(estado=EstadoPedido.CREANDO)
    return render(request, 'listar_pedidos.html', {'pedidos': pedidos})


def crear_pedido(request):
    if request.method == 'POST':
        form = PedidoForm(request.POST)
        if form.is_valid():
            pedido = form.save()
            return redirect('editar_pedido', pedido_id=pedido.id)
    else:
        form = PedidoForm()
    return render(request, 'crear_pedido.html', {'form': form})

def pedido_enviado(request):
    return render(request, 'pedido_enviado.html')


@require_POST
def eliminar_pedido(request, pedido_id):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Autenticación requerida'}, status=403)
    pedido = get_object_or_404(Pedido, pk=pedido_id)
    pedido.delete()
    return JsonResponse({'mensaje': 'Pedido eliminado'})


def editar_pedido(request, pedido_id):
    pedido = get_object_or_404(Pedido, id=pedido_id)
    if request.method == 'POST':
        form = DetallePedidoForm(request.POST)
        if form.is_valid():
            detalle_pedido = form.save(commit=False)
            detalle_pedido.pedido = pedido
            detalle_pedido.save()
            return redirect('editar_pedido', pedido_id=pedido.id)
    else:
        form = DetallePedidoForm()
    
    return render(request, 'editar_pedido.html', {'form': form, 'pedido': pedido})


def eliminar_detalle_pedido(request, detalle_id):
    if request.method == 'POST':
        detalle = get_object_or_404(DetallePedido, id=detalle_id)
        pedido_id = detalle.pedido.id
        detalle.delete()
        return redirect('editar_pedido', pedido_id=pedido_id)
    return redirect('editar_pedido', pedido_id=detalle.pedido.id)


@csrf_exempt
def enviar_pedido(request, pedido_id):
    if request.method == 'POST':
        pedido = get_object_or_404(Pedido, pk=pedido_id)
        pedido.estado = EstadoPedido.EN_ESPERA
        pedido.save()
        return JsonResponse({'success': True}, status=200)
    return JsonResponse({'error': 'Método no permitido'}, status=405)


def ver_pedidos(request):
    pedidos_en_espera = Pedido.objects.filter(estado=EstadoPedido.EN_ESPERA)
    pedidos_aceptados = Pedido.objects.filter(estado=EstadoPedido.ACEPTADO)
    pedidos_terminados = Pedido.objects.filter(estado=EstadoPedido.TERMINADO)
    pedidos_rechazados = Pedido.objects.filter(estado=EstadoPedido.RECHAZADO)
    
    return render(request, 'ver_pedidos.html', {
        'pedidos_en_espera': pedidos_en_espera,
        'pedidos_aceptados': pedidos_aceptados,
        'pedidos_terminados': pedidos_terminados,
        'pedidos_rechazados': pedidos_rechazados
    })


def cambiar_estado_pedido(request, pedido_id, nuevo_estado):
    pedido = get_object_or_404(Pedido, id=pedido_id)
    pedido.estado = nuevo_estado
    pedido.save()
    return redirect('ver_pedidos')


def gestionar_pedido(request, pedido_id):
    pedido = get_object_or_404(Pedido, id=pedido_id)
    
    if request.method == 'POST':
        form = PedidoForm(request.POST, instance=pedido)
        if form.is_valid():
            form.save()
            return redirect('ver_pedidos')
    else:
        form = PedidoForm(instance=pedido)
    
    return render(request, 'gestionar_pedido.html', {'form': form, 'pedido': pedido})


@login_required
def perfil(request):
    try:
        cliente = ClienteRegistrado.objects.get(user=request.user)
    except ClienteRegistrado.DoesNotExist:
        # Redirige al usuario a una página para completar su perfil, o muestra un mensaje de error
        return redirect('crear_perfil')  # Suponiendo que tienes una vista para crear el perfil del cliente

    return render(request, 'perfil.html', {'cliente': cliente})


def editar_perfil(request):
    cliente = ClienteRegistrado.objects.get(user=request.user)
    if request.method == 'POST':
        form = ClienteEditForm(request.POST, instance=cliente)
        if form.is_valid():
            form.save()
            return redirect('perfil')
    else:
        form = ClienteEditForm(instance=cliente)
    return render(request, 'editar_perfil.html', {'form': form})


def agregar_tarjeta(request):
    cliente = ClienteRegistrado.objects.get(user=request.user)
    if request.method == 'POST':
        form = TarjetaForm(request.POST)
        if form.is_valid():
            tarjeta = form.save(commit=False)
            tarjeta.cliente = cliente
            tarjeta.save()
            return redirect('perfil')
    else:
        form = TarjetaForm()
    return render(request, 'agregar_tarjeta.html', {'form': form})


def editar_tarjeta(request, tarjeta_id):
    cliente = request.user.clienteregistrado
    tarjeta = cliente.tarjeta_credito
    
    if request.method == 'POST':
        form = TarjetaForm(request.POST, instance=tarjeta)
        if form.is_valid():
            form.save()
            return redirect('perfil')
    else:
        form = TarjetaForm(instance=tarjeta)
    
    return render(request, 'editar_tarjeta.html', {'form': form})


@login_required
def pedidos_en_proceso(request):
    cliente = request.user.clienteregistrado
    pedidos_en_espera = Pedido.objects.filter(estado=EstadoPedido.EN_ESPERA)
    pedidos_aceptados = Pedido.objects.filter(estado=EstadoPedido.ACEPTADO)
    pedidos_terminados = Pedido.objects.filter(estado=EstadoPedido.TERMINADO)
    pedidos_rechazados = Pedido.objects.filter(estado=EstadoPedido.RECHAZADO)
    
    return render(request, 'proceso_pedido.html', {
        'pedidos_en_espera': pedidos_en_espera,
        'pedidos_aceptados': pedidos_aceptados,
        'pedidos_terminados': pedidos_terminados,
        'pedidos_rechazados': pedidos_rechazados
    })


@login_required
def realizar_pago_cliente(request, pedido_id):
    pedido = get_object_or_404(Pedido, id=pedido_id, cliente=request.user.clienteregistrado)

    if request.method == 'POST':
        form = PagoForm(request.POST)
        if form.is_valid():
            pago = form.save(commit=False)
            pago.pedido = pedido
            pago.cliente = request.user.clienteregistrado
            pago.monto = pedido.calcular_precio_aproximado()
            pago.save()
            pedido.estado = Pedido.EstadoPedido.TERMINADO  # Asumiendo que el pago cambia el estado a terminado
            pedido.save()
            return redirect('pedidos_en_proceso')
    else:
        form = PagoForm()

    return render(request, 'realizar_pago_cliente.html', {'form': form, 'pedido': pedido})


@login_required
def realizar_pago(request, pedido_id):
    pedido = get_object_or_404(Pedido, id=pedido_id)

    if request.method == 'POST':
        form = PagoForm(request.POST)
        if form.is_valid():
            pago = form.save(commit=False)
            pago.pedido = pedido
            pago.cliente = request.user.clienteregistrado
            pago.monto = pedido.calcular_precio_aproximado()  # Asumiendo que tienes este método en el modelo Pedido
            pago.save()
            pedido.estado = 'PAGADO'  # Actualiza el estado del pedido
            pedido.save()
            return redirect('ver_pedidos')  # Redirige a la vista de pedidos
    else:
        form = PagoForm()

    return render(request, 'realizar_pago.html', {'form': form, 'pedido': pedido})


def listar_ropa(request):
    prendas = Ropa.objects.all()
    return render(request, 'listar_ropa.html', {'prendas': prendas})


@require_POST
def eliminar_ropa(request, ropa_id):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Autenticación requerida'}, status=403)
    ropa = get_object_or_404(Ropa, pk=ropa_id)
    ropa.delete()
    return JsonResponse({'mensaje': 'Ropa eliminada'})


def crear_ropa(request):
    if request.method == 'POST':
        form = RopaForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('listar_ropa')
    else:
        form = RopaForm()
    return render(request, 'crear_ropa.html', {'form': form})


def editar_ropa(request, ropa_id):
    prenda = get_object_or_404(Ropa, pk=ropa_id)
    if request.method == 'POST':
        form = RopaForm(request.POST, instance=prenda)
        if form.is_valid():
            form.save()
            return redirect('listar_ropa')
    else:
        form = RopaForm(instance=prenda)
    return render(request, 'editar_ropa.html', {'form': form})




