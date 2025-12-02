from django.db import models

class Service(models.Model):
    title = models.CharField(
        'Título do Serviço',
        max_length=120
    )

    description = models.TextField(
        'Descrição do Serviço',
        max_length=300,
        blank=True
    )

    icon = models.CharField(
        'Ícone (Emoji ou classe CSS)',
        max_length=50,
        help_text="Ex: 💰 ou fas fa-file-invoice"
    )

    link = models.URLField(
        'Link de Acesso',
        blank=True,
        null=True
    )

    is_active = models.BooleanField(
        'Ativo',
        default=True
    )

    order = models.PositiveIntegerField(
        'Ordem de Exibição',
        default=0
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        verbose_name = 'Serviço'
        verbose_name_plural = 'Serviços'
        ordering = ['order']

    def __str__(self):
        return self.title
