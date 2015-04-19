from rest_framework import serializers
from machine import models

class DockerHostSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.DockerHost
        exclude = ('cert_pem', 'key_pem', 'ca_pem')

