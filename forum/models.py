from django.db import models

import datetime
from django.utils import timezone
class Anuncio(models.Model):
    titulo = models.CharField(max_length=200)
    descricao = models.TextField()
    preco = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    imagem_url = models.URLField(blank=True, null=True)
    vendedor = models.CharField(max_length=200, default="anônimo")
    data_criacao = models.DateTimeField("Criado em ", auto_now_add=True)

    def __str__(self):
        return f"[{self.id}] {self.titulo} - {self.vendedor}"

    
