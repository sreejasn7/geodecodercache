from django.contrib import admin

# Register your models here.
from .models import GeoDecodderCache

class GeoDecodderCacheAdmin(admin.ModelAdmin):
    pass
admin.site.register(GeoDecodderCache,GeoDecodderCacheAdmin)