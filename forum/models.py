from django.db import models
from django.contrib.auth.models import User


class Anuncio(models.Model):
    titulo = models.CharField(max_length=200)
    descricao = models.TextField()
    preco = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    imagem_url = models.URLField(blank=True, null=True)
    vendedor = models.CharField(max_length=200, default='anônimo')
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='anuncios', null=True, blank=True)
    contato = models.CharField(max_length=30, blank=True, null=True)
    data_criacao = models.DateTimeField('Criado em', auto_now_add=True)

    def __str__(self):
        return f'[{self.id}] {self.titulo} - {self.vendedor}'


class Comentario(models.Model):
    anuncio = models.ForeignKey(Anuncio, on_delete=models.CASCADE, related_name='comentarios')
    autor = models.ForeignKey('auth.User', on_delete=models.CASCADE, null=True, blank=True)
    texto = models.TextField()
    resposta_vendedor = models.TextField(blank=True, null=True)
    data_criacao = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        autor_nome = self.autor.username if self.autor else 'Anônimo'
        return f'{autor_nome} em [{self.anuncio.id}]'
