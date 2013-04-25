from PackageHandlers import PackageHandler
from django.db.models.signals import pre_delete, pre_save, post_save, post_syncdb

from AppDistribution.models import *

from django.contrib.auth import models as auth_app, get_user_model
from django.contrib.auth.models import User
from AppDistribution.models import *




def delete_app(sender, instance, signal, *args, **kwargs):
    app_file = "%s/%s.ipa" % (settings.MEDIA_ROOT, instance.uuid)
    try:
        remove(app_file)
    except OSError:
        pass

def save_app(sender, instance, signal, *args, **kwargs):

    handler = PackageHandler(instance.package, instance)
    handler.handle()

pre_save.connect(save_app, sender=App)
pre_delete.connect(delete_app, sender=App)
