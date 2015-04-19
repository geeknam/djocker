from rest_framework import viewsets
from compose import models
from compose.serializers import ServiceSerializer, DeploymentSerializer
from rest_framework.decorators import detail_route


class ServiceViewSet(viewsets.ModelViewSet):

    queryset = models.Service.objects.all()
    serializer_class = ServiceSerializer



class DeploymentViewSet(viewsets.ModelViewSet):

    queryset = models.Deployment.objects.all()
    serializer_class = DeploymentSerializer


    @detail_route(methods=['get', 'post'])
    def views(self, request, pk=None):
        pass