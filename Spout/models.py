from django.conf import settings
from django.db import models
from django.db.models.signals import pre_delete

from os import remove

import utils


class App(models.Model):

    APP_TYPE_CHOICES = (("ANDROID", "Android"),
                    ("IOS", "iOS"),
                    ("BLACKBERRY", "BlackBerry"))

    def __unicode__(self):
        return "%s - %s" % (self.name, self.version)
    class Meta:
        unique_together = (('version', 'name'),)

    version = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    product = models.ForeignKey('Product')
    note = models.CharField(max_length=255)
    comment = models.CharField(max_length=255, blank=True, null=True)
    creation_date = models.DateTimeField()
    approved = models.BooleanField(default=True)
    device_type = models.CharField(choices=APP_TYPE_CHOICES, default="IOS", max_length=255)
    uuid = models.CharField(max_length=255, blank=True, null=True, unique=True)
    tags = models.ManyToManyField('Tag')

class Tag(models.Model):

    def __unicode__(self):
        return self.name

    name = models.CharField(max_length=255)
    description = models.CharField(max_length=255)

class Product(models.Model):

    def __unicode__(self):
        return self.name

    name = models.CharField(max_length=255)

class Crash(models.Model):
    uuid = models.ForeignKey(App, to_field="uuid")
    body = models.TextField()

def delete_app(sender, instance, signal, *args, **kwargs):

    app_file = utils.ipa_path(instance.name, instance.version)
    print app_file
    try:
        remove(app_file)
    except OSError:
        pass

pre_delete.connect(delete_app, sender=App)
