from rest_framework import serializers
from compose import models
from machine.serializers import DockerHostSerializer

class ServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Service


class DeploymentSerializer(serializers.ModelSerializer):

    service = ServiceSerializer()
    host = DockerHostSerializer()

    class Meta:
        model = models.Deployment
