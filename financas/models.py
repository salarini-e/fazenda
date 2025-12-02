from django.db import models
from django.contrib.auth.models import User
# Create your models here.
class Servico(models.Model):
    class Meta:
        verbose_name = 'Serviço'
        verbose_name_plural = "Serviços"
        ordering = ['id', 'titulo']

         
    titulo = models.CharField(max_length=150)
    descricao = models.CharField(max_length=255, blank=True)
    link = models.URLField(blank=True)
    
    icone = models.CharField(
        max_length=50,
        help_text="Ex: fa-file-invoice, fa-balance-scale, fa-comments",
    )
    # banner = models.ImageField(upload_to = 'cursos_livres/media/banner/', null=True)
    ordem = models.PositiveIntegerField(default=0)
    ativo = models.BooleanField(default=True)
    

    dt_inclusao = models.DateTimeField(auto_now_add=True, editable=False)
    dt_alteracao = models.DateField(auto_now=True)

    user_inclusao = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ServicoUserInclusao')
    user_ultima_alteracao = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ServicoUserAlteracao', null=True, blank=True)

    def __str__(self):
        return '%s' % (self.titulo)
