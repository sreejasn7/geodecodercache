from django.shortcuts import render
from django.http import HttpResponse ,  JsonResponse
from home.transactions import validate_cache , save_cache , update_cache
import requests
from django.views import View
from xml.etree import ElementTree

 
class ReverseGeoDecoder(View):

    def get(self,request,*args, **kwargs):
        '''
        Description : 
            This is the core function. All the functionalities revolve around this function. The get function is called in the url /get_address/<lat>/<long>
        Flow - 
            1. On receiving a new lat and long, it checkes that if its a new entry or expired entry via `validate_cache`
            2. In both cases , of a new entry or expired entry , the trigger to `fetch_nominatim` is done.
            3. In case of a new entry , the data from the API is saved to DB via `save_cache`
            4. In case of an expired entry , the new name and current datetime is set to the DB via function `update_cache`
            5. In case of a lat and long request which exists in DB as well as the date has not been expired , then data from the DB is fetched
        '''

        lat = kwargs['lat']
        long = kwargs['long']
        output_json = {}

        # On receiving a new lat and long, it checkes that if its a new entry or expired entry via `validate_cache`
        new_cordinates , (cordinates_mobj ,can_update_cache) = validate_cache(lat , long)
        
        if (new_cordinates or can_update_cache):
            #In both cases , of a new entry or expired entry , the trigger to `fetch_nominatim` is done.
            output = self.fetch_nominatim(requests , lat , long)
            if can_update_cache: 
                #In case of an expired entry , the new name and current datetime is set to the DB via function `update_cache`
                update_cache(cordinates_mobj,output['name'])
            elif new_cordinates: 
                #In case of a new entry , the data from the API is saved to DB via `save_cache`
                save_cache(output['name'], lat , long)
            output_json = output
            
        else:
            #In case of a lat and long request which exists in DB as well as the date has not been expired , then data from the DB is fetched
            output_json['name'] = cordinates_mobj.name
            
        return JsonResponse(output_json, safe=False)

    def fetch_nominatim(self,requests=None , lat=None, long=None): 
        '''
        Description:
            This function fetches the nominatim data. 
        '''
        output = ''
        url = "https://nominatim.openstreetmap.org/reverse"
        response = requests.get(url = url, params = {'lat':lat , 'lon':long})
        if response.status_code == 200:
            tree = ElementTree.fromstring(response.content)
            addressparttree = tree.find('addressparts')
            avoid_tags = ['country_code' , 'amenity']
            for element in addressparttree:
                if element.tag not in avoid_tags:
                    output += element.text
                    output += ' '
        return {'name' : output}
        



