
from .models import GeoDecodderCache
from datetime import datetime

EXPIRE_HOURS = 24

def validate_cache(lat , long):
    hours = 0
    update_cache = False
    geodecoder_mobj = GeoDecodderCache.objects.filter(lat = lat , long = long).first()
    if geodecoder_mobj is not None:
        duration = datetime.now() - geodecoder_mobj.date
        duration_in_seconds = duration.total_seconds()
        hours = divmod(duration_in_seconds, 3600)[0]
        if hours >= EXPIRE_HOURS:
            update_cache = True

    return geodecoder_mobj == None ,(geodecoder_mobj , update_cache)

def save_cache(name,lat ,long):
    try:
        now = datetime.now()
        geodecodercache_model_obj = GeoDecodderCache(lat = lat , long = long , name=name , date = now)
        geodecodercache_model_obj.save()
        return {'save':True}
    except:
        return {'save':False}


def update_cache(model_obj , name):
    try:
        model_obj.date = datetime.now()
        model_obj.name = name
        model_obj.save()
        return {'update':True}
    except:
        return {'update':False}