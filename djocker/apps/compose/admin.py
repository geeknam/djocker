from django.contrib import admin
from compose import models


class CommandAdmin(admin.ModelAdmin):

    list_display = ('instruction', 'argument')

admin.site.register(models.Command, CommandAdmin)


class CommandInline(admin.StackedInline):
    model = models.CommandOrder
    extra = 0

class DockerfileAdmin(admin.ModelAdmin):
    readonly_fields = ('content', 'image_id')
    inlines = [
        CommandInline
    ]

admin.site.register(models.Dockerfile, DockerfileAdmin)

admin.site.register(models.Service)
admin.site.register(models.Stack)


def start_deployment(modeladmin, request, queryset):
    deployment = queryset.first()
    deployment.start()

class DeploymentAdmin(admin.ModelAdmin):

    actions = [
        start_deployment
    ]

admin.site.register(models.Deployment, DeploymentAdmin)
