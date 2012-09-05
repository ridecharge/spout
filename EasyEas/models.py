from django.conf import settings
from django.db import models
from django.db.models.signals import pre_delete

from os import remove

import utils

class App(models.Model):

    def __unicode__(self):
        return "%s - %s" % (self.name, self.version)
    class Meta:
        unique_together = (('version', 'name'),)

    version = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    product = models.ForeignKey('Product')
    note = models.CharField(max_length=255)
    creation_date = models.DateTimeField()
    approved = models.BooleanField(default=True)

class Product(models.Model):

    def __unicode__(self):
        return self.name

    name = models.CharField(max_length=255)


def delete_app(sender, instance, signal, *args, **kwargs):

    app_file = utils.ipa_path(instance.name, instance.version)
    print app_file
    try:
        remove(app_file)
    except OSError:
        pass

pre_delete.connect(delete_app, sender=App)
