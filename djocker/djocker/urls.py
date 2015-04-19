from django.conf.urls import patterns, include, url
from django.contrib import admin
from rest_framework.routers import DefaultRouter
from compose.views import ServiceViewSet, DeploymentViewSet
from machine.views import DockerHostViewSet

router = DefaultRouter()
router.register(r'services', ServiceViewSet)
router.register(r'deployments', DeploymentViewSet)
router.register(r'hosts', DockerHostViewSet)


urlpatterns = patterns('',

    url(r'^api/', include(router.urls)),

    url(r'^grappelli/', include('grappelli.urls')),
    url(r'^admin/', include(admin.site.urls)),

)
