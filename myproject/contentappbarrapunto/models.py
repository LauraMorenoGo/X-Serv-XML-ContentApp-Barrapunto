from django.db import models

class Pages(models.Model):  #Misma clase que en Django_cms
    name = models.CharField(max_length=32)
    page = models.TextField()
