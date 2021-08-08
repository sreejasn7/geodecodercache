from django.db import models

# Create your models here.

class GeoDecodderCache(models.Model):
    lat = models.FloatField(default=None)
    long = models.FloatField(default=None)
    name = models.CharField(max_length=200)
    date = models.DateTimeField()

    def __str__(self):
        return str(self.lat) + ' | ' + str(self.long)