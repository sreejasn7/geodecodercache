
from django.urls import path , re_path , register_converter
from home.views import ReverseGeoDecoder , index
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from utils import converters
register_converter(converters.FloatConverter, 'float')


urlpatterns = [
     path('',index, name='index'),
    path('get_address/<float:lat>/<float:long>/', ReverseGeoDecoder.as_view(), name='get_address'),
] 

urlpatterns += staticfiles_urlpatterns()