from django.db import models


# Create your models here.
class Page(models.Model):
    href = models.CharField('href', max_length=1000)
    title = models.CharField('title', max_length=1000)
