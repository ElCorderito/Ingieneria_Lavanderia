from django import forms
from django.contrib.auth.models import User
from django.db.models import Q
from .models import *
from django.forms import inlineformset_factory


class UsuarioForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())

    class Meta:
        model = User
        fields = ['username', 'email', 'password']


class ClienteForm(forms.ModelForm):
    class Meta:
        model = ClienteRegistrado
        fields = ['user', 'dir_cliente', 'colonia_cliente', 'codigo_postal', 'tel_cliente', 'fecha_nacimiento', 'tarjeta_credito']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['user'].queryset = User.objects.filter(is_superuser=False).exclude(Q(clienteregistrado__isnull=False) | Q(repartidor__isnull=False))


class RepartidorForm(forms.ModelForm):
    class Meta:
        model = Repartidor
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['user'].queryset = User.objects.filter(is_superuser=False).exclude(Q(clienteregistrado__isnull=False) | Q(repartidor__isnull=False))


class ClienteEditForm(forms.ModelForm):
    class Meta:
        model = ClienteRegistrado
        exclude = ['user']


class PedidoForm(forms.ModelForm):
    class Meta:
        model = Pedido
        fields = ['cliente', 'servicio', 'estado']

    def __init__(self, *args, **kwargs):
        super(PedidoForm, self).__init__(*args, **kwargs)
        self.fields['servicio'].queryset = Servicio.objects.all()
        self.fields['cliente'].queryset = ClienteRegistrado.objects.all()

    def calcular_total(self):
        total = 0
        detalles = self.detalles.all()
        for detalle in detalles:
            total += detalle.cantidad * (detalle.ropa.precio + (self.servicio.precio_adicional if self.servicio else 0))
        return total

class DetallePedidoForm(forms.ModelForm):
    class Meta:
        model = DetallePedido
        fields = ['ropa', 'cantidad']

    def __init__(self, *args, **kwargs):
        super(DetallePedidoForm, self).__init__(*args, **kwargs)
        self.fields['ropa'].queryset = Ropa.objects.all()
        

class TarjetaForm(forms.ModelForm):
    class Meta:
        model = Tarjeta
        fields = ['nom_titular', 'num_tarjeta', 'fecha_ven_tarjeta', 'nip_tarjeta']


class PagoForm(forms.ModelForm):
    class Meta:
        model = Pago
        fields = ['cliente', 'pedido', 'fecha_pago', 'monto', 'metodo_pago']
        widgets = {
            'metodo_pago': forms.Select(choices=[('Tarjeta de Crédito', 'Tarjeta de Crédito'), ('PayPal', 'PayPal')])
        }


class RopaForm(forms.ModelForm):
    class Meta:
        model = Ropa
        fields = ['nombre', 'precio']

