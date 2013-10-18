from django.conf import settings
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.contrib.humanize.templatetags import humanize
from django.template.defaultfilters import slugify
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType


from bitfield import BitField

from django.contrib.sites.models import Site

from os import remove
from os.path import splitext


APP_TYPE_CHOICES = (("ANDROID", "Android"),
                    ("IOS", "iOS"),
                    ("BLACKBERRY", "BlackBerry"))

GROUP_BY_CHOICES = (("product", "Product"),
                  ("tag", "Tag"))

SITE_CACHE = {}

class SpoutSiteManager(models.Manager):

    def get_current(self):
        """
        Returns the current ``Site`` based on the SITE_ID in the
        project's settings. The ``Site`` object is cached the first
        time it's retrieved from the database.
        """
        from django.conf import settings
        try:
            sid = settings.SITE_ID
        except AttributeError:
            from django.core.exceptions import ImproperlyConfigured
            raise ImproperlyConfigured("You're using the Django \"sites framework\" without having set the SITE_ID setting. Create a site in your database and set the SITE_ID setting to fix this error.")
        try:
            current_site = SITE_CACHE[sid]
        except KeyError:
            current_site = self.get(pk=sid)
            SITE_CACHE[sid] = current_site
        return current_site

    def clear_cache(self):
        """Clears the ``Site`` object cache."""
        global SITE_CACHE
        SITE_CACHE = {}


class SpoutSite(models.Model):

    domain = models.CharField('domain name', max_length=100)
    name = models.CharField('display name', max_length=50)
    home_page = models.ForeignKey('Page', null=True)



    objects = SpoutSiteManager()

    class Meta:
        verbose_name = 'site'
        verbose_name_plural = 'sites'
        ordering = ('domain',)

    def __str__(self):
        return self.domain

    def save(self, *args, **kwargs):
        super(SpoutSite, self).save(*args, **kwargs)
        # Cached information will likely be incorrect now.
        if self.id in SITE_CACHE:
            del SITE_CACHE[self.id]

    def delete(self):
        pk = self.pk
        super(Site, self).delete()
        try:
            del SITE_CACHE[pk]
        except KeyError:
            pass


class App(models.Model):

    def __unicode__(self):
        return "%s - %s" % (self.name, self.version)


    download_count = models.IntegerField(default=0)
    product = models.ForeignKey('Product')
    tags = models.ManyToManyField('Tag', related_name='apps', blank=True, null=True)
    note = models.CharField(max_length=255, blank=True, null=True)

    icon = models.ImageField(upload_to=settings.APP_ICON_ROOT, blank=True, null=True)
    version = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    creation_date = models.DateTimeField()
    device_type = models.CharField(choices=APP_TYPE_CHOICES, default="IOS", max_length=255) #TODO This should be a function, not stored

    def _formatted_age(self):
        return humanize.naturaltime(self.creation_date)
    def _icon_url(self):

        try:

            if self.icon.url != None:
                return self.icon.url.replace(settings.MEDIA_ROOT, "/media")
        except ValueError:
                return ""

    icon_url = property(_icon_url)
    formatted_age = property(_formatted_age)
 
class AppAsset(models.Model):

    def __unicode__(self):
        return self.asset_file.name

    def save(self):
        extension = splitext(asset_file.name)
        asset_type = AssetType.get_or_create(extension)
        super(AssetType, self).save(*args, **kwargs)

    app = models.ForeignKey('App', related_name='assets', null=True)

    primary = models.BooleanField()
    uuid = models.CharField(max_length=255, null=True, blank=True)
    asset_type = models.ForeignKey('AssetType', null=True)
    asset_file = models.FileField(upload_to=settings.APP_PACKAGE_ROOT)

       
class AssetType(models.Model):

    @classmethod
    def get_or_create(self, extension):

        try:
            asset_type = AssetType.objects.get(extension=extension)
        except AssetType.DoesNotExist:
            asset_type = AssetType(extension=extension)

        return asset_type

    name = models.CharField(max_length=255, blank=True, null=True)
    extension = models.CharField(max_length=10)

class Tag(models.Model):

    def __unicode__(self):
        return self.name

    def _short_description(self):
        return self.description if len(self.description) > 0 else self.name

    short_description = property(_short_description)
    name = models.CharField(max_length=255)
    description = models.CharField(max_length=255, blank=True, null=True)

class Product(models.Model):

    def __unicode__(self):
        return self.name
    name = models.CharField(max_length=255)

class PageRow(models.Model):

    def __unicode__(self):
        if self.show_options.tag:
            return "%s - %s" % (self.product.name, self.tag.name)
        else:
            return self.product.name

    page = models.ForeignKey('Page')
    product = models.ForeignKey(Product)
    tag = models.ForeignKey(Tag, blank=True, null=True)

    show_options = BitField(flags=('tag', 
                                   'age', 
                                   'version', 
                                   'more_versions',))


    def _get_app(self):
        """ Returns the most recent app associated with the page row """
        try:
            app = App.objects.filter(product=self.product, tags=self.tag).latest("creation_date")
        except:
            app = None

        return app

    app = property(_get_app)

class Page(models.Model):

    def __unicode__(self):
        return self.title

    title = models.CharField(max_length=255)
    heading = models.CharField(max_length=255, blank=True, null=True)
    top_html = models.TextField(blank=True, null=True)
    slug = models.SlugField()
    requires_auth = models.BooleanField()
    expiration_date = models.DateTimeField(blank=True, null=True)
    group_by = models.CharField(choices=GROUP_BY_CHOICES, max_length=100, blank=True, null=True)

    def _pagerows(self):
        if self.group_by != None:
            rows = self.pagerow_set.all().order_by(self.group_by)
        else:
            rows = self.pagerow_set.all()

        return rows

    pagerows = property(_pagerows)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        super(Page, self).save(*args, **kwargs)

class SpoutUserManager(BaseUserManager):

    def create_user(self, username, password):
        
        user = self.model(
                username = username,
        )


        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password):

        user = self.create_user(
            username=username,
            password=password,
        )

        user.is_admin = True
        user.save(using=self._db)
        return user

class SpoutUser(AbstractBaseUser):

    username = models.CharField(max_length=100, unique=True)
    first_name = models.CharField(max_length=100, null=True)
    last_name = models.CharField(max_length=100, null=True)

    class Meta:
        verbose_name = 'user'
        verbose_name_plural = 'users'
        ordering = ['username']

 
    email = models.EmailField(
        verbose_name='email address',
        max_length=255,
        null=True,
        blank=True,
        unique=True,
        db_index=True,
    )

    expiration_date = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    main_page = models.ForeignKey(Page, related_name='users', null=True)
    allowed_pages = models.ManyToManyField(Page, related_name='user_allowed_pages', null=True)

    objects = SpoutUserManager()

    USERNAME_FIELD='username'

    def save(self, *args, **kwargs):
      super(SpoutUser, self).save(*args, **kwargs)
      if self.main_page:
            self.allowed_pages.add(self.main_page)

    def get_full_name(self):
        return "%s %s" % (self.first_name, self.last_name)

    def get_short_name(self):
        return self.first_name

    def __unicode__(self):
        return self.username

    def has_perm(self, perm, obj=None):
        #TODO do this properly
        return True

    def has_module_perms(self, app_label):
        #TODO do this properly
        return True

    @property
    def is_staff(self):
        return self.is_admin

    @is_staff.setter
    def is_staff(self, value):
        self.is_admin = value

class Setting(models.Model):
    name = models.CharField(max_length=100)
    value = models.CharField(max_length=500)
    value_type = models.CharField(max_length=1, choices=(('s','string'),('i','integer'),('b','boolean')))

    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey()

    def actual_value(self):
        types = {
            's': str, 
            'i':int, 
            'b': (lambda v: v.lower().startswith('t') or v.startswith('1'))
        }
        return types[self.value_type](self.value)

