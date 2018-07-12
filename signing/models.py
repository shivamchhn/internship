from django.db import models


class Detail(models.Model):
    firstname = models.CharField(max_length=100)
    lastname = models.CharField(max_length=100)
    date_of_birth = models.DateField()
    address1 = models.CharField(max_length=200)
    address2 = models.CharField(max_length=200)

