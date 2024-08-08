from .models import *
from rest_framework import serializers

class CurrencySerializer(serializers.ModelSerializer):
    class Meta:
        model = Currency
        fields = ['currency_name','currency_symbol']

class CurrencyValueMappingSerializer(serializers.ModelSerializer):
    currency = CurrencySerializer()
    class Meta:
        model = CurrencyValueMapping
        fields = ['currency','value']