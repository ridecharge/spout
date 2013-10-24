from django.db.models.signals import pre_delete, pre_save, post_save, post_syncdb

from AppDistribution.models import *

from AppDistribution.PackageHandlers import PackageHandler
from django.contrib.auth import models as auth_app, get_user_model
from django.contrib.auth.models import User
from AppDistribution.models import *
from datetime import datetime 




def delete_app(sender, instance, signal, *args, **kwargs):
    try:
        for asset in instance.assets.all():
            remove(asset.asset_file.name)

    except OSError:
        pass

def save_app(sender, instance, signal, *args, **kwargs):

    if instance.primary is True:
        handler = PackageHandler(instance)
        handler.handle()


post_save.connect(save_app, sender=AppAsset)
pre_delete.connect(delete_app, sender=App)
