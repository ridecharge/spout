# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding M2M table for field tags on 'App'
        db.create_table('EasyEas_app_tags', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('app', models.ForeignKey(orm['EasyEas.app'], null=False)),
            ('tag', models.ForeignKey(orm['EasyEas.tag'], null=False))
        ))
        db.create_unique('EasyEas_app_tags', ['app_id', 'tag_id'])


    def backwards(self, orm):
        # Removing M2M table for field tags on 'App'
        db.delete_table('EasyEas_app_tags')


    models = {
        'EasyEas.app': {
            'Meta': {'unique_together': "(('version', 'name'),)", 'object_name': 'App'},
            'approved': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'creation_date': ('django.db.models.fields.DateTimeField', [], {}),
            'device_type': ('django.db.models.fields.CharField', [], {'default': "'IOS'", 'max_length': '255'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'note': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'product': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['EasyEas.Product']"}),
            'tags': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['EasyEas.Tag']", 'symmetrical': 'False'}),
            'version': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'EasyEas.product': {
            'Meta': {'object_name': 'Product'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'EasyEas.tag': {
            'Meta': {'object_name': 'Tag'},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        }
    }

    complete_apps = ['EasyEas']