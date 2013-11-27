from django.db.models.signals import pre_delete, pre_save, post_save, post_syncdb

from AppDistribution.models import *

from AppDistribution.PackageHandlers import PackageHandler
from django.contrib.auth import models as auth_app, get_user_model
from django.contrib.auth.models import User
from AppDistribution.models import *
from datetime import datetime 
from hashlib import md5




def delete_app(sender, instance, signal, *args, **kwargs):
    try:
        for asset in instance.assets.all():
            remove(asset.asset_file.name)

    except OSError:
        pass

def post_save_asset(sender, instance, signal, *args, **kwargs):

    if instance.primary is True:
        asset_file = open(instance.asset_file.path)
        file_hash = md5(asset_file.read())
        if instance.file_hash != file_hash.hexdigest(): 
            handler = PackageHandler(instance)
            handler.handle()

    if instance.asset_type == None:
        extension = splitext(instance.asset_file.name)
        instance.asset_type = AssetType.get_or_create(extension[1])
        instance.save()




post_save.connect(post_save_asset, sender=AppAsset)
pre_delete.connect(delete_app, sender=App)
