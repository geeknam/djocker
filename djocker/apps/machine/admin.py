from django.contrib import admin
from machine import models
from compose.models import Deployment


class DeploymentInline(admin.StackedInline):
    model = Deployment
    extra = 0


class DockerHostAdmin(admin.ModelAdmin):

    list_display = ('name', 'ip_address')
    readonly_fields = ('images', )
    inlines = [
        DeploymentInline
    ]

    def images(self, instance):
        return '\n'.join([
            ', '.join(image['RepoTags']) for image in instance.images
        ])

admin.site.register(models.DockerHost, DockerHostAdmin)

admin.site.register(models.Container)