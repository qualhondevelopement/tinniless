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


class SettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Settings
        fields = '__all__'

class FeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feedback
        fields = '__all__'

class MusicCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = MusicCategory
        fields = '__all__'

class MusicFilesSerializer(serializers.ModelSerializer):
    class Meta:
        model = MusicFiles
        fields = '__all__'