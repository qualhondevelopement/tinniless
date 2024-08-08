from django.shortcuts import render
from users.models import *
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.db import transaction
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
import json
from .utils import *
from users.utils import *
from users.serializers import *
from .serializers import *
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
        

class GetTaxDocumentTypes(APIView):
    def get(self,request,format =None):
        doc_types = DOCUMENT_TYPES
        return Response(
            {
                "success":"Data Fetched",
                "data":doc_types
            }
        )
    

class ManageSettings(APIView):
    authentication_classes = [JwtAuthentication,]
    def patch(self,request,*args,**kwargs):
        user = request.user
        if user.user_type != UserAccount.ADMIN:
            return Response(
                {
                    "error":"User is not an admin"
                },
                400
            )
        settings_id = request.data.get('settings_id')
        try:
            settings_obj = Settings.objects.get(id=settings_id)
            serializer = SettingsSerializer(settings_obj,data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data,status=status.HTTP_400_BAD_REQUEST) 
            return Response({
                "error":serializer.errors
                },
                status=status.HTTP_400_BAD_REQUEST) 
        except Settings.DoesNotExist:
            return Response({
                'error':'Setting not found'
                },
                status=status.HTTP_400_BAD_REQUEST)
        
    def get(self,request,*args,**kwargs):
        user = request.user
        if user.user_type != UserAccount.ADMIN:
            return Response(
                {
                    "error":"User is not an admin"
                },
                400
            )
        settings_id = request.query_params.get('settings_id')
        try:
            setting_obj = Settings.objects.get(id=settings_id)
            serializer = SettingsSerializer(setting_obj)
             
            return Response({
                "success":"Data Fetched",
                "data":serializer.data
                },
                status=status.HTTP_200_OK) 
        except Settings.DoesNotExist:
            return Response({
                'error':'Setting not found'
                },
                status=status.HTTP_400_BAD_REQUEST)
        
class ManageFeedback(APIView):
    authentication_classes = [JwtAuthentication,]
    def post(self,request,*args,**kwargs):
        user = request.user
        if user.user_type != UserAccount.ADMIN:
            return Response(
                {
                    "error":"User is not an admin"
                },
                400
            )
        serializer = FeedbackSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data,status=status.HTTP_200_OK) 
        return Response({
            "error":serializer.errors
            },
            status=status.HTTP_400_BAD_REQUEST) 

    def patch(self,request,*args,**kwargs):
        user = request.user
        if user.user_type != UserAccount.ADMIN:
            return Response(
                {
                    "error":"User is not an admin"
                },
                400
            )
        feedback_id = request.data.get('feedback_id')
        try:
            feedback_obj = Feedback.objects.get(id=feedback_id)
            serializer = FeedbackSerializer(feedback_obj,data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data,status=status.HTTP_200_OK) 
            return Response({
                "error":serializer.errors
                },
                status=status.HTTP_400_BAD_REQUEST) 
        except Settings.DoesNotExist:
            return Response({
                'error':'Feedback not found'
                },
                status=status.HTTP_400_BAD_REQUEST)
        
    def get(self,request,*args,**kwargs):
        user = request.user
        if user.user_type != UserAccount.ADMIN:
            return Response(
                {
                    "error":"User is not an admin"
                },
                400
            )
        feedback_id = request.query_params.get('feedback_id')
        try:
            feedback_obj = Feedback.objects.get(id=feedback_id)
            serializer = FeedbackSerializer(feedback_obj)
             
            return Response({
                "success":"Data Fetched",
                "data":serializer.data
                },
                status=status.HTTP_200_OK) 
        except Settings.DoesNotExist:
            return Response({
                'error':'Feedback not found'
                },
                status=status.HTTP_400_BAD_REQUEST)
        
    def delete(self,request,*args,**kwargs):
        user = request.user
        if user.user_type != UserAccount.ADMIN:
            return Response(
                {
                    "error":"User is not an admin"
                },
                400
            )
        feedback_id = request.query_params.get('feedback_id')
        try:
            feedback_obj = Feedback.objects.get(id=feedback_id)
            feedback_obj.is_deleted = True
            feedback_obj.save()
            return Response({
                "success":"Feedback has been deleted.",
                },
                status=status.HTTP_200_OK) 
        except Settings.DoesNotExist:
            return Response({
                'error':'Feedback not found'
                },
                status=status.HTTP_400_BAD_REQUEST)