import os
from django.db import models
from django.db.models.signals import pre_delete 
from django.dispatch import receiver
from docker import Client
from docker.tls import TLSConfig

class DockerHost(models.Model):

    name = models.CharField(max_length=100)
    ip_address = models.GenericIPAddressField(null=False, blank=False)
    port = models.PositiveIntegerField()
    cert_pem = models.TextField()
    key_pem = models.TextField()
    ca_pem = models.TextField()

    def __unicode__(self):
        return self.name

    @property
    def host(self):
        return '%s:%d' % (self.ip_address, self.port)

    def write_to_fs(self):
        path = '/tmp/%s' % self.name
        if not os.path.exists(path):
            os.makedirs(path)
            cert_pem_file = open(os.path.join(path, 'cert.pem'), 'wb')
            cert_pem_file.write(self.cert_pem)

            key_pem_file = open(os.path.join(path, 'key.pem'), 'wb')
            key_pem_file.write(self.key_pem)

            ca_pem_file = open(os.path.join(path, 'ca.pem'), 'wb')
            ca_pem_file.write(self.ca_pem)
        return path

    @property
    def client(self):
        path = self.write_to_fs()
        tls_config = TLSConfig(
            client_cert=('%s/cert.pem' % path, '%s/key.pem' % path),
            verify='%s/ca.pem' % path, assert_hostname=False
        )
        return Client(
            base_url='https://%s' % self.host,
            tls=tls_config,
        )

    @property
    def images(self):
        return self.client.images()


class Container(models.Model):

    container_id = models.CharField(max_length=200)
    service = models.ForeignKey('compose.Service')
    status = models.CharField(max_length=200, blank=True, null=True)
    host = models.ForeignKey('machine.DockerHost', related_name='containers')

    def __unicode__(self):
        return '%s - %s' % (self.container_id, self.service.image)

    def save(self, *args, **kwargs):
        if self.container_id:
            containers = self.host.client.containers()
            for c in containers:
                if c['Id'] == self.container_id:
                    self.status = c['Status']
        super(Container, self).save(*args, **kwargs)


@receiver(pre_delete, sender=Container)
def remove_container(sender, instance, **kwargs):
    instance.host.client.stop(container=instance.container_id)
    instance.host.client.remove_container(container=instance.container_id)

