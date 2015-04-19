from rest_framework import viewsets
from machine import models
from machine.serializers import DockerHostSerializer
from rest_framework.decorators import detail_route
from rest_framework.response import Response

class DockerHostViewSet(viewsets.ModelViewSet):

    queryset = models.DockerHost.objects.all()
    serializer_class = DockerHostSerializer

    @detail_route(methods=['get'])
    def containers(self, request, pk=None):
        host = self.get_object()
        containers = host.client.containers()
        return Response(containers)


    @detail_route(methods=['get'])
    def images(self, request, pk=None):
        host = self.get_object()
        images = host.client.images()
        return Response(images)