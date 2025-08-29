from django.db import models

class Modulo(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()
    imagen = models.ImageField(upload_to='modulos/')

    def __str__(self):
        return self.nombre
