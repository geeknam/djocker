from django.db import models
from django.contrib.postgres.fields import ArrayField, HStoreField
from machine.models import Container
import yaml
from io import BytesIO


class Command(models.Model):

    instruction = models.CharField(max_length=100)
    argument = models.TextField(null=False, blank=False)

    def __unicode__(self):
        return '%s %s' % (self.instruction, self.argument)

    def to_line(self):
        return '%s %s' % (self.instruction, self.argument)


class CommandOrder(models.Model):
    command = models.ForeignKey('Command')
    dockerfile = models.ForeignKey('Dockerfile')
    order = models.PositiveIntegerField(blank=True, null=True)


class Dockerfile(models.Model):

    name = models.CharField(max_length=200)
    image_tag = models.CharField(max_length=200,
        help_text='Format: image_name:tag_name'
    )
    commands = models.ManyToManyField('Command', through='CommandOrder')

    def __unicode__(self):
        return self.name

    @property
    def content(self):
        return '\n'.join(
            [command.to_line() for command in self.commands.all()]
        )

    @property
    def image_id(self):
        return '\n'.join(
            self._client.images(name=self.image_tag.split(':')[0], quiet=True)
        )


class Service(models.Model):

    image = models.CharField(max_length=200)
    stack = models.ForeignKey('Stack', related_name='services', null=True, blank=True)
    dockerfile = models.ForeignKey('Dockerfile', null=True, blank=True)
    name = models.CharField(max_length=200)
    command = models.CharField(max_length=200, null=True, blank=True)
    detach = models.BooleanField(default=True)
    memory_limit = models.CharField(max_length=100)
    ports = HStoreField(blank=True, null=True)
    links = HStoreField(blank=True, null=True)
    environment = HStoreField(blank=True, null=True)

    def __unicode__(self):
        return '%s - %s' % (self.name, self.image)


class Deployment(models.Model):

    service = models.ForeignKey('Service')
    host = models.ForeignKey('machine.DockerHost', related_name='deployments')
    force_pull = models.BooleanField(default=False,
        help_text='Downloads any updates to the FROM image in Dockerfile'
    )
    remove_containers = models.BooleanField(default=False,
        help_text='Always remove intermediate containers, even after unsuccessful builds'
    )

    def __unicode__(self):
        return '%s - %s' % (self.host, self.service)

    def build_image(self):
        f = BytesIO(self.dockerfile.content.encode('utf-8'))
        cli = self.host.client
        response = [line for line in cli.build(
            fileobj=f, rm=True, tag=self.dockerfile.image_tag
        )]
        return response

    def prepare_image(self):
        if self.service.dockerfile:
            return self.build_image()
        return self.host.client.pull(self.service.image)

    def start(self):
        response = self.prepare_image()
        print response
        container = self.host.client.create_container(
            image=self.service.image,
            name=self.service.name,
            detach=self.service.detach,
            mem_limit=self.service.memory_limit,
            ports=self.service.ports,
            environment=self.service.environment,
            command=self.service.command
        )
        self.host.client.start(
            container=container.get('Id'),
            port_bindings=self.service.ports
        )
        container = Container.objects.create(
            container_id=container.get('Id'),
            host=self.host,
            service=self.service
        )
        return container


class Stack(models.Model):

    name = models.CharField(max_length=200)
    definition = models.TextField()

    def __unicode__(self):
        return self.name

    @staticmethod
    def flatten_env(env_list):
        env_dict = {}
        for env in env_list:
            env_dict.update(env)
        return env_dict

    @staticmethod
    def map_ports(port_list):
        port_dict = {}
        for port in port_list:
            mapping = port.split(':')
            if len(mapping) > 1:
                port_dict[mapping[0]] = mapping[1]
            else:
                port_dict[mapping[0]] = None
        return port_dict

    def create_services(self):
        composition = yaml.load(self.definition)
        for service_name, definition in composition.items():
            service, created = Service.objects.get_or_create(
                name='%s_%s' % (self.name, service_name),
                defaults={
                    'image': definition['image'],
                    'memory_limit': '512m',
                    'environment': Stack.flatten_env(definition.get('environment', [])),
                    'ports': Stack.map_ports(definition.get('ports', [])),
                    'stack': self
                }
            )
