from django.shortcuts import render
from users.models import *
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.db import transaction
from rest_framework.response import Response
from django.conf import settings
import json
from .utils import *
from users.serializers import *
# Create your views here.


class GetLocation(APIView):
    def get(self,request,format = None):
        country =request.query_params.get("country",None)
        state  = request.query_params.get("state",None)
        country_json = {}
        json_path = settings.COUNTRY_JSON
        with open(json_path, 'r', encoding='utf-8') as file:
            country_json =  json.load(file)
        resp_dict = {}
        if not country:
            resp_dict = {
                "countries":[c['name'] for c in country_json]
            }
        elif country and not state:
            for c in country_json:
                if c['name'].lower() == country.lower():
                    resp_dict={
                        "states":[s['name'] for s in c['states']]
                    }
        elif country and state:
            for c in country_json:
                if c['name'].lower() == country.lower():
                    for s in c['states']:
                        if s['name'].lower() == state.lower():
                            resp_dict = {
                                "cities":[c['name'] for c in s['cities']]
                            }
        else:
            resp_dict = {}
            
        return Response(resp_dict,200)                  
                            
class GetAllTinitusTypes(APIView):
    def get(self,request,format = None):
        return Response(
            {
                "data":return_all_tinnitus_types()
            },
            200
        )
        
        
class GetAllLanguage(APIView):
    def get(self,request,format = None):
        langs = Language.objects.all()
        lang_serializer = LanguageSerializer(langs,many = True)
        return Response(
            {
                "success":"Data Fetched",
                "data":lang_serializer.data
            },
            200
        )