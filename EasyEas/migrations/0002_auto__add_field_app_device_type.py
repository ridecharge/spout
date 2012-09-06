# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'App.device_type'
        db.add_column('EasyEas_app', 'device_type',
                      self.gf('django.db.models.fields.CharField')(default='IOS', max_length=255),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'App.device_type'
        db.delete_column('EasyEas_app', 'device_type')


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
            'version': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'EasyEas.product': {
            'Meta': {'object_name': 'Product'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        }
    }

    complete_apps = ['EasyEas']