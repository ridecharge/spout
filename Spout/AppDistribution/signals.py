from PackageHandlers import PackageHandler
from django.db.models.signals import pre_delete, pre_save, post_save, post_syncdb

from AppDistribution.models import *

from django.contrib.auth import models as auth_app, get_user_model
from AppDistribution.models import *




def auto_create_superuser(*args, **kwargs):


    main_page = Page(title="First Page", heading="Welcome!", top_html="Welcome to Spout!  You haven't configured your site to have a main page yet.  A page is the place where your apps are displayed to users both on the Spout native client and on the web.  Go to <yoursitedomain>/admin to set this up!  Thanks for using Spout!", requires_auth=False)
    main_page.save()
    

    site = SpoutSite(domain="http://example.com", name="Example Site", home_page=main_page)
    site.save()

    user = SpoutUser.objects.create_superuser("SpoutAdmin", "imakeapps")
    user.save()

post_syncdb.connect(auto_create_superuser,
    sender=auth_app, dispatch_uid="django.contrib.auth.management.create_superuser")

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
