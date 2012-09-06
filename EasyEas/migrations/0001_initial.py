# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'App'
        db.create_table('EasyEas_app', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('version', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('product', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['EasyEas.Product'])),
            ('note', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('creation_date', self.gf('django.db.models.fields.DateTimeField')()),
            ('approved', self.gf('django.db.models.fields.BooleanField')(default=True)),
        ))
        db.send_create_signal('EasyEas', ['App'])

        # Adding unique constraint on 'App', fields ['version', 'name']
        db.create_unique('EasyEas_app', ['version', 'name'])

        # Adding model 'Product'
        db.create_table('EasyEas_product', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal('EasyEas', ['Product'])


    def backwards(self, orm):
        # Removing unique constraint on 'App', fields ['version', 'name']
        db.delete_unique('EasyEas_app', ['version', 'name'])

        # Deleting model 'App'
        db.delete_table('EasyEas_app')

        # Deleting model 'Product'
        db.delete_table('EasyEas_product')


    models = {
        'EasyEas.app': {
            'Meta': {'unique_together': "(('version', 'name'),)", 'object_name': 'App'},
            'approved': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'creation_date': ('django.db.models.fields.DateTimeField', [], {}),
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