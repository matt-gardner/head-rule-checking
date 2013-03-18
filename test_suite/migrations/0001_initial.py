# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Category'
        db.create_table('test_suite_category', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('symbol', self.gf('django.db.models.fields.CharField')(max_length=32)),
        ))
        db.send_create_signal('test_suite', ['Category'])

        # Adding model 'TestSuite'
        db.create_table('test_suite_testsuite', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('category', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['test_suite.Category'])),
            ('version', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal('test_suite', ['TestSuite'])

        # Adding model 'Expansion'
        db.create_table('test_suite_expansion', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('test_suite', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['test_suite.TestSuite'])),
            ('rule', self.gf('django.db.models.fields.CharField')(max_length=1024)),
            ('supa_example', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('penn_example', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('index', self.gf('django.db.models.fields.IntegerField')()),
            ('count', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal('test_suite', ['Expansion'])

        # Adding model 'Annotation'
        db.create_table('test_suite_annotation', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('expansion', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['test_suite.Expansion'])),
            ('head_correct', self.gf('django.db.models.fields.NullBooleanField')(null=True, blank=True)),
            ('comp_head_correct', self.gf('django.db.models.fields.NullBooleanField')(null=True, blank=True)),
            ('notes', self.gf('django.db.models.fields.TextField')(blank=True)),
        ))
        db.send_create_signal('test_suite', ['Annotation'])

        # Adding model 'Comment'
        db.create_table('test_suite_comment', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('annotation', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['test_suite.Annotation'])),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('comment', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal('test_suite', ['Comment'])


    def backwards(self, orm):
        # Deleting model 'Category'
        db.delete_table('test_suite_category')

        # Deleting model 'TestSuite'
        db.delete_table('test_suite_testsuite')

        # Deleting model 'Expansion'
        db.delete_table('test_suite_expansion')

        # Deleting model 'Annotation'
        db.delete_table('test_suite_annotation')

        # Deleting model 'Comment'
        db.delete_table('test_suite_comment')


    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'test_suite.annotation': {
            'Meta': {'object_name': 'Annotation'},
            'comp_head_correct': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'expansion': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['test_suite.Expansion']"}),
            'head_correct': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'notes': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        },
        'test_suite.category': {
            'Meta': {'ordering': "['symbol']", 'object_name': 'Category'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'symbol': ('django.db.models.fields.CharField', [], {'max_length': '32'})
        },
        'test_suite.comment': {
            'Meta': {'object_name': 'Comment'},
            'annotation': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['test_suite.Annotation']"}),
            'comment': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        },
        'test_suite.expansion': {
            'Meta': {'object_name': 'Expansion'},
            'count': ('django.db.models.fields.IntegerField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'index': ('django.db.models.fields.IntegerField', [], {}),
            'penn_example': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'rule': ('django.db.models.fields.CharField', [], {'max_length': '1024'}),
            'supa_example': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'test_suite': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['test_suite.TestSuite']"})
        },
        'test_suite.testsuite': {
            'Meta': {'object_name': 'TestSuite'},
            'category': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['test_suite.Category']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'version': ('django.db.models.fields.IntegerField', [], {})
        }
    }

    complete_apps = ['test_suite']