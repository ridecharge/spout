# -*- coding: utf-8 -*-
from south.db import db
from south.v2 import SchemaMigration
from django.db import models
from AppDistribution.models import *
import datetime


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'SpoutSite'
        db.create_table(u'AppDistribution_spoutsite', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('domain', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('home_page', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['AppDistribution.Page'], null=True)),
        ))
        db.send_create_signal(u'AppDistribution', ['SpoutSite'])

        # Adding model 'AppAsset'
        db.create_table(u'AppDistribution_appasset', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('notes', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('asset_file', self.gf('django.db.models.fields.files.FileField')(max_length=100)),
        ))
        db.send_create_signal(u'AppDistribution', ['AppAsset'])

        # Adding model 'App'
        db.create_table(u'AppDistribution_app', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('package', self.gf('django.db.models.fields.files.FileField')(max_length=100)),
            ('download_count', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('product', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['AppDistribution.Product'])),
            ('note', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('icon', self.gf('django.db.models.fields.files.ImageField')(max_length=100, null=True, blank=True)),
            ('version', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('creation_date', self.gf('django.db.models.fields.DateTimeField')()),
            ('device_type', self.gf('django.db.models.fields.CharField')(default='IOS', max_length=255)),
            ('uuid', self.gf('django.db.models.fields.CharField')(max_length=255, unique=True, null=True, blank=True)),
        ))
        db.send_create_signal(u'AppDistribution', ['App'])

        # Adding M2M table for field assets on 'App'
        db.create_table(u'AppDistribution_app_assets', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('app', models.ForeignKey(orm[u'AppDistribution.app'], null=False)),
            ('appasset', models.ForeignKey(orm[u'AppDistribution.appasset'], null=False))
        ))
        db.create_unique(u'AppDistribution_app_assets', ['app_id', 'appasset_id'])

        # Adding M2M table for field tags on 'App'
        db.create_table(u'AppDistribution_app_tags', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('app', models.ForeignKey(orm[u'AppDistribution.app'], null=False)),
            ('tag', models.ForeignKey(orm[u'AppDistribution.tag'], null=False))
        ))
        db.create_unique(u'AppDistribution_app_tags', ['app_id', 'tag_id'])

        # Adding model 'AssetType'
        db.create_table(u'AppDistribution_assettype', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('extension', self.gf('django.db.models.fields.CharField')(max_length=10)),
        ))
        db.send_create_signal(u'AppDistribution', ['AssetType'])

        # Adding model 'Tag'
        db.create_table(u'AppDistribution_tag', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal(u'AppDistribution', ['Tag'])

        # Adding model 'Product'
        db.create_table(u'AppDistribution_product', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal(u'AppDistribution', ['Product'])

        # Adding model 'PageRow'
        db.create_table(u'AppDistribution_pagerow', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('page', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['AppDistribution.Page'])),
            ('product', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['AppDistribution.Product'])),
            ('tag', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['AppDistribution.Tag'])),
            ('show_more_versions', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('show_tag', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('show_age', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal(u'AppDistribution', ['PageRow'])

        # Adding model 'Page'
        db.create_table(u'AppDistribution_page', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('heading', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('top_html', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('slug', self.gf('django.db.models.fields.SlugField')(max_length=50)),
            ('requires_auth', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('expiration_date', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
        ))
        db.send_create_signal(u'AppDistribution', ['Page'])

        # Adding model 'SpoutUser'
        db.create_table(u'AppDistribution_spoutuser', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('password', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('last_login', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('username', self.gf('django.db.models.fields.CharField')(unique=True, max_length=100)),
            ('first_name', self.gf('django.db.models.fields.CharField')(max_length=100, null=True)),
            ('last_name', self.gf('django.db.models.fields.CharField')(max_length=100, null=True)),
            ('email', self.gf('django.db.models.fields.EmailField')(db_index=True, max_length=255, unique=True, null=True, blank=True)),
            ('expiration_date', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('is_active', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('is_admin', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('main_page', self.gf('django.db.models.fields.related.ForeignKey')(related_name='users', null=True, to=orm['AppDistribution.Page'])),
        ))
        db.send_create_signal(u'AppDistribution', ['SpoutUser'])

        # Adding M2M table for field allowed_pages on 'SpoutUser'
        db.create_table(u'AppDistribution_spoutuser_allowed_pages', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('spoutuser', models.ForeignKey(orm[u'AppDistribution.spoutuser'], null=False)),
            ('page', models.ForeignKey(orm[u'AppDistribution.page'], null=False))
        ))
        db.create_unique(u'AppDistribution_spoutuser_allowed_pages', ['spoutuser_id', 'page_id'])

        # Adding model 'Setting'
        db.create_table(u'AppDistribution_setting', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('value', self.gf('django.db.models.fields.CharField')(max_length=500)),
            ('value_type', self.gf('django.db.models.fields.CharField')(max_length=1)),
            ('content_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['contenttypes.ContentType'])),
            ('object_id', self.gf('django.db.models.fields.PositiveIntegerField')()),
        ))
        db.send_create_signal(u'AppDistribution', ['Setting'])

        # Adding model 'Crash'
        db.create_table(u'AppDistribution_crash', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('uuid', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['AppDistribution.App'], to_field='uuid')),
            ('body', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal(u'AppDistribution', ['Crash'])

    def backwards(self, orm):
        # Deleting model 'SpoutSite'
        db.delete_table(u'AppDistribution_spoutsite')

        # Deleting model 'AppAsset'
        db.delete_table(u'AppDistribution_appasset')

        # Deleting model 'App'
        db.delete_table(u'AppDistribution_app')

        # Removing M2M table for field assets on 'App'
        db.delete_table('AppDistribution_app_assets')

        # Removing M2M table for field tags on 'App'
        db.delete_table('AppDistribution_app_tags')

        # Deleting model 'AssetType'
        db.delete_table(u'AppDistribution_assettype')

        # Deleting model 'Tag'
        db.delete_table(u'AppDistribution_tag')

        # Deleting model 'Product'
        db.delete_table(u'AppDistribution_product')

        # Deleting model 'PageRow'
        db.delete_table(u'AppDistribution_pagerow')

        # Deleting model 'Page'
        db.delete_table(u'AppDistribution_page')

        # Deleting model 'SpoutUser'
        db.delete_table(u'AppDistribution_spoutuser')

        # Removing M2M table for field allowed_pages on 'SpoutUser'
        db.delete_table('AppDistribution_spoutuser_allowed_pages')

        # Deleting model 'Setting'
        db.delete_table(u'AppDistribution_setting')

        # Deleting model 'Crash'
        db.delete_table(u'AppDistribution_crash')


    models = {
        u'AppDistribution.app': {
            'Meta': {'object_name': 'App'},
            'assets': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['AppDistribution.AppAsset']", 'symmetrical': 'False'}),
            'creation_date': ('django.db.models.fields.DateTimeField', [], {}),
            'device_type': ('django.db.models.fields.CharField', [], {'default': "'IOS'", 'max_length': '255'}),
            'download_count': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'icon': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'note': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'package': ('django.db.models.fields.files.FileField', [], {'max_length': '100'}),
            'product': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['AppDistribution.Product']"}),
            'tags': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'apps'", 'symmetrical': 'False', 'to': u"orm['AppDistribution.Tag']"}),
            'uuid': ('django.db.models.fields.CharField', [], {'max_length': '255', 'unique': 'True', 'null': 'True', 'blank': 'True'}),
            'version': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        u'AppDistribution.appasset': {
            'Meta': {'object_name': 'AppAsset'},
            'asset_file': ('django.db.models.fields.files.FileField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'notes': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'})
        },
        u'AppDistribution.assettype': {
            'Meta': {'object_name': 'AssetType'},
            'extension': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        u'AppDistribution.crash': {
            'Meta': {'object_name': 'Crash'},
            'body': ('django.db.models.fields.TextField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'uuid': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['AppDistribution.App']", 'to_field': "'uuid'"})
        },
        u'AppDistribution.page': {
            'Meta': {'object_name': 'Page'},
            'expiration_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'heading': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'requires_auth': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '50'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'top_html': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'})
        },
        u'AppDistribution.pagerow': {
            'Meta': {'object_name': 'PageRow'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'page': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['AppDistribution.Page']"}),
            'product': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['AppDistribution.Product']"}),
            'show_age': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'show_more_versions': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'show_tag': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'tag': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['AppDistribution.Tag']"})
        },
        u'AppDistribution.product': {
            'Meta': {'object_name': 'Product'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        u'AppDistribution.setting': {
            'Meta': {'object_name': 'Setting'},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'object_id': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'value': ('django.db.models.fields.CharField', [], {'max_length': '500'}),
            'value_type': ('django.db.models.fields.CharField', [], {'max_length': '1'})
        },
        u'AppDistribution.spoutsite': {
            'Meta': {'ordering': "('domain',)", 'object_name': 'SpoutSite'},
            'domain': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'home_page': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['AppDistribution.Page']", 'null': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'AppDistribution.spoutuser': {
            'Meta': {'ordering': "['username']", 'object_name': 'SpoutUser'},
            'allowed_pages': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "'user_allowed_pages'", 'null': 'True', 'to': u"orm['AppDistribution.Page']"}),
            'email': ('django.db.models.fields.EmailField', [], {'db_index': 'True', 'max_length': '255', 'unique': 'True', 'null': 'True', 'blank': 'True'}),
            'expiration_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_admin': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True'}),
            'main_page': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'users'", 'null': 'True', 'to': u"orm['AppDistribution.Page']"}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100'})
        },
        u'AppDistribution.tag': {
            'Meta': {'object_name': 'Tag'},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        }
    }

    complete_apps = ['AppDistribution']
