# from django.test import TestCase

from django.test import RequestFactory, TestCase
from home.views import ReverseGeoDecoder
from requests.exceptions import Timeout
from unittest.mock import Mock
import json
from home.models import GeoDecodderCache
from datetime import datetime




class GeodecoderTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.lat = -34.4391708
        self.long = -58.7064573

    def test_mock_fetch_nominatim(self, requests=None , lat= None ,long=None):
        '''
        Description-  Use mocks to verify Nominatim calls.
            1. Mocking the function `fetch_nominatim` (from the class ReverseGeoDecoder)
            2. Idea is to mock the request and responses to and from the function `fetch_nominatim`. The response is set with status code and default content. 
            Based on the environment of request and responses set  `fetch_nominatim` behaves accordingly.
        Flow - 
            1. Create Mock Responses 
            2. Set Mock Status code and Contents 
            3. Set Requests timeout
            4. Asserting the timeout error in calling fetch_nominatim
            5. Asserting that the output of fetch_nominatim will be based on response_mock.content
        params -  
            request: requests object
            lat = latitude
            long = longitude
        output - 
            Based on the response of the xml content set , the output will be '1 333 Khaf County Razavi Khorasan Iran '
        '''
        # Mock requests object created
        requests = Mock()

        # Http response object created. Status code  , content has been set.
        response_mock = Mock()
        response_mock.status_code = 200
        response_mock.content = "<reversegeocode timestamp='Sun, 08 Aug 21 04:55:32 +0000'><addressparts><city>1</city><district>333</district><county>Khaf County</county><state>Razavi Khorasan</state><country>Iran</country></addressparts></reversegeocode>"
        
        # Set Requests timeout
        requests.get.side_effect = [Timeout, response_mock]
        
        #Calling the View Class Reverse Geo Decoder to mock the function fetch nominatim
        geo_obj = ReverseGeoDecoder()
        
        # Asserting the timeout Error
        with self.assertRaises(Timeout):
            geo_obj.fetch_nominatim(requests, lat=self.lat, long = self.long)
        
        #Fetching the output from mock response set
        output = geo_obj.fetch_nominatim(requests, lat=self.lat, long=self.long)['name']
        
        #Asserting that the output of fetch_nominatim will be based on response_mock.content
        assert output == '1 333 Khaf County Razavi Khorasan Iran '

        #Returning output for further use in the below test cases.
        return {'name':output}

    
    def test_save_cache(self , lat=None,long = None):
       
        '''
        Description- A value which is not present in DB will trigger a call to Nominatim
            1. To test the view function `get` (from the class GeoDecodderCache) and check is the value is getting saved to DB
        Flow of Asserting - 
            1. Asserting that there is no initial object saved for the lat and long
            2. Calling the ReverseGeoDecoder `get` function to save the new values for lat and long
            3. In order to bypass the actual `fetch_nominatim` calling , it is replaced with `test_mock_fetch_nominatim`
            4. After saving the new object , asserting that the newly saved cache has the same name as the output from `test_mock_fetch_nominatim`
            5. After saving the new object , asserting that the saved cache object is the prescribed format in models. Format  str(self.lat) + ' | ' + str(self.long)
            6. Asserting the response status code
        '''
        if lat is not None:
            self.lat = lat 
        if long is not None:
            self.long = long

        #Asserting that there is no initial object saved for the lat and long
        assert GeoDecodderCache.objects.filter(lat = self.lat , long=self.long).first() == None
        
        request =  self.factory.get('/get_address/')

        #calling the class ReverseGeoDecoder
        reverse_geo_coder = ReverseGeoDecoder()

        #In order to bypass the actual `fetch_nominatim` calling , it is replaced with `test_mock_fetch_nominatim`
        reverse_geo_coder.fetch_nominatim = self.test_mock_fetch_nominatim

        #Calling the ReverseGeoDecoder `get` function to save the new values for lat and long
        response = reverse_geo_coder.get(request , lat=self.lat , long=self.long)
        response_dict = eval(response.content)
        geodecoder_mobj = GeoDecodderCache.objects.filter(name = response_dict['name']).first()
        
        #After saving the new object , asserting that the newly saved cache has the same name as the output from `test_mock_fetch_nominatim`
        assert geodecoder_mobj.name == '1 333 Khaf County Razavi Khorasan Iran '

        #After saving the new object , asserting that the saved cache object is the prescribed format in models. Format  str(self.lat) + ' | ' + str(self.long)
        self.assertEqual(geodecoder_mobj.__str__() , str(self.lat) + ' | ' + str(self.long))

        # Asserting the response status code
        assert response.status_code == 200

        return geodecoder_mobj.name


    def test_no_trigger_nominatim(self):
        '''
        Description- A subsequent call for same value wont trigger a call to Nominatim
            1. To test if the function `fetch_nominatim` is not triggered.
        Flow of Asserting - 
            1. Calling the function test_save_cache to save a new DB entry.
            2. After saving the new object , asserting that the newly saved cache has the same name as the output from `test_save_cache`
            3. In order to test is the fetch_nominatim is not called , set fetch_nominatim to None and see if any expection arises. 
               If exception does not arise, it means that the fetch_nominatim has not been triggered.
            4. Calling the get function to check if the function is returing a response corresponding to lat and long
            5. Assering that output from the `test_save_cache` and ReverseGeoDecoder `get` function is the same
        '''

        #Calling the function test_save_cache to save a new DB entry.
        name = self.test_save_cache(self.lat,self.long)

        #After saving the new object , asserting that the newly saved cache has the same name as the output from `test_save_cache`
        assert GeoDecodderCache.objects.filter(name = name).first() != None

        request =  self.factory.get('/get_address/')
        reverse_geo_coder = ReverseGeoDecoder()

        # In order to test is the fetch_nominatim is not called , set fetch_nominatim to None and see if any expection arises. 
        #If exception does not arise, it means that the fetch_nominatim has not been triggered.
        reverse_geo_coder.fetch_nominatim = None
        response = reverse_geo_coder.get(request , lat=self.lat , long=self.long)
        response_dict = eval(response.content)
        
        #Assering that output from the `test_save_cache` and ReverseGeoDecoder `get` function is the same
        assert response_dict['name'] == name


    def test_trigger_nominatim_for_24hours(self):
        '''
        Description- A call for a value which is present in DB but is older than a day will trigger a call to Nominatim.
            1. To test if the function `fetch_nominatim` is not triggered.
        Flow of Asserting - 
            1. Calling the function test_save_cache to save a new DB entry.
            2. After saving the new object , asserting that the newly saved cache has the same name as the output from `test_save_cache`
            3. Validate the hours of the saved cache and the current date time and check if less than 24 hours
            4. Set a new date which is 26 hours greater than the saved cache time
            5.In order to test is the fetch_nominatim is called , set fetch_nominatim to None and see if any expection arises. 
                If exception arise, it means that the fetch_nominatim has been triggered.
            6. Assertion check raised as when it searches for fetch_nominatim ,  received None in its place.If none is received then fetch_nominatim was triggered 
        '''
        EXPIRE_HOURS = 24
        #Calling the function test_save_cache to save a new DB entry.
        name = self.test_save_cache(self.lat,self.long)

        #After saving the new object , asserting that the newly saved cache has the same name as the output from `test_save_cache`
        geo_obj = GeoDecodderCache.objects.filter(name = name).first()
        assert geo_obj != None
        duration = datetime.now() - geo_obj.date
        duration_in_seconds = duration.total_seconds()
        hours = divmod(duration_in_seconds, 3600)[0]
        
        #Validate the hours of the saved cache and the current date time and check if less than 24 hours
        assert hours <= EXPIRE_HOURS
        
        #Set a new date which is 26 hours greater than the saved cache time
        geo_date = geo_obj.date
        date_at_26hours = datetime(geo_date.year, geo_date.month , geo_date.day-1,geo_date.hour-2,geo_date.minute , geo_date.second)
        duration = geo_obj.date - date_at_26hours
        duration_in_seconds = duration.total_seconds()
        hours = divmod(duration_in_seconds, 3600)[0]
        assert hours > EXPIRE_HOURS
        geo_obj.date = date_at_26hours 
        geo_obj.save()
        

        try:
            reverse_geo_coder = ReverseGeoDecoder()
            # In order to test is the fetch_nominatim is called , set fetch_nominatim to None and see if any expection arises. 
            # If exception arise, it means that the fetch_nominatim has been triggered.
            request =  self.factory.get('/get_address/')
            reverse_geo_coder.fetch_nominatim = None
            response_code = reverse_geo_coder.get(request , lat=self.lat , long=self.long) 

        except Exception as e:
            #Assertion check raised as when it searches for fetch_nominatim ,  received None in its place.If none is received then fetch_nominatim was triggered
            assert 'NoneType' in str(e)
       
       
        

       







