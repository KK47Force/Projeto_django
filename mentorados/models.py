from django.db import models
from django.contrib.auth.models import User
from datetime import datetime, timedelta
import secrets

class Navigators(models.Model):
    nome = models.CharField(max_length=255)
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return self.nome

# Create your models here.
class Mentorados(models.Model):
    estagio_choices = (
        ('E-1', '10-100K'),
        ('E-2', '100-500K'),
        ('E-3', '500-1KK'),
    )
    nome = models.CharField(max_length=255)
    criado_em = models.DateField(auto_now_add=True)
    foto = models.ImageField(upload_to='fotos', blank=True, null=True)
    estagio = models.CharField(max_length=3, choices=estagio_choices)
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    navigator = models.ForeignKey(Navigators, on_delete=models.CASCADE, blank=True, null=True)
    token = models.CharField(max_length=16, null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.token:
            self.token = self.gerar_token_unico()
        super().save(*args, **kwargs)

    
    def gerar_token_unico(self):
        while True:
            token = secrets.token_urlsafe(8)
            if not Mentorados.objects.filter(token=token).exists():
                return token

    def __str__(self):
        return self.nome
    

class DisponibilidadeHorarios(models.Model):
    data_inicial = models.DateTimeField(null=True, blank=True)
    mentor = models.ForeignKey(User, on_delete=models.CASCADE)
    agendado = models.BooleanField(default=False)

    def data_final(self):
        return self.data_inicial + timedelta(minutes=50)
    

class Reuniao(models.Model):
    tag_choices = (
        ('G', 'Gestão'),
        ('M', 'Marketing'),
        ('RH', 'Gestão de pessoas'),
        ('I', 'Impostos')
    )
    data = models.ForeignKey(DisponibilidadeHorarios, on_delete=models.CASCADE)
    mentorado = models.ForeignKey(Mentorados, on_delete=models.CASCADE)
    tag = models.CharField(max_length=2, choices=tag_choices)
    descricao = models.TextField()


class Tarefa(models.Model):
    mentorado = models.ForeignKey(Mentorados, on_delete=models.DO_NOTHING)
    tarefa = models.CharField(max_length=255)
    realizada = models.BooleanField(default=False)


class Upload(models.Model):
    mentorado = models.ForeignKey(Mentorados, on_delete=models.DO_NOTHING)
    video = models.FileField(upload_to='video')


