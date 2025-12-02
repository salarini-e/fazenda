from django.db import models
from autenticacao.models import User, Pessoa

class TentativaBurla(models.Model):
    local_deteccao = models.CharField(max_length=250)
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Usuário')
    ip_address = models.GenericIPAddressField(verbose_name='Endereço IP')
    data_tentativa = models.DateTimeField(auto_now_add=True, verbose_name='Data da Tentativa')
    informacoes_adicionais = models.TextField(blank=True, null=True, verbose_name='Informações Adicionais')
    
    class Meta:
        verbose_name = 'Usuário suspeito de tentar burla o sistema'
        verbose_name_plural = 'Usuários suspeitos de tentar burla o sistema'

    def __str__(self):
        return f'{self.user.username} - {self.data_tentativa} - {self.local_deteccao}'
