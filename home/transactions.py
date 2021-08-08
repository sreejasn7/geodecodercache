
from .models import GeoDecodderCache
from datetime import datetime

EXPIRE_HOURS = 24

def validate_cache(lat , long):
    '''
    Description : Validate cache function is called to check the expire hours.
    params - 
        lat - latitude
        long - longitude
    '''
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
    '''
    Description : Save cache function saves new API calls to DB 
    params - 
        name - The name fetched from the API call
        lat - latitude
        long - longitude
    '''
    try:
        now = datetime.now()
        geodecodercache_model_obj = GeoDecodderCache(lat = lat , long = long , name=name , date = now)
        geodecodercache_model_obj.save()
        return {'save':True}
    except:
        return {'save':False}


def update_cache(model_obj , name):
    '''
    Description : Update cache function updates date and name to the DB
    params - 
        model_obj - The model object to be saved
        name - The new name fetched from the API
    '''
    try:
        model_obj.date = datetime.now()
        model_obj.name = name
        model_obj.save()
        return {'update':True}
    except:
        return {'update':False}