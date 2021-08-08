from django.shortcuts import render
from django.http import HttpResponse ,  JsonResponse
from home.transactions import validate_cache , save_cache , update_cache
# from home.http_requests import fetch_nominatim
import requests
from django.views import View
from xml.etree import ElementTree


# Create your views here.
def analysis_data(request):
    return render(request, "analysis.html")

class ReverseGeoDecoder(View):

    def get(self,request,*args, **kwargs):
        lat = kwargs['lat']
        long = kwargs['long']
        output_json = {}
        
        new_cordinates , (cordinates_mobj ,can_update_cache) = validate_cache(lat , long)
        if (new_cordinates or can_update_cache):
            output = self.fetch_nominatim(requests , lat , long)
            if can_update_cache: 
                update_cache(cordinates_mobj,output['name'])
            elif new_cordinates: 
                save_cache(output['name'], lat , long)
            output_json = output
        else:
            output_json['name'] = cordinates_mobj.name
            
        return JsonResponse(output_json, safe=False)

    def fetch_nominatim(self,requests=None , lat=None, long=None): 
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
        



