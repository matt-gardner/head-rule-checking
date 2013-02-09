from django.db import models

from collections import defaultdict
from collections import namedtuple

class Category(models.Model):
    symbol = models.CharField(max_length=32)

    def __unicode__(self):
        return self.symbol

    def versions(self):
        return self.testsuite_set.order_by('version')


class TestSuite(models.Model):
    category = models.ForeignKey('Category')
    version = models.IntegerField()

    def __unicode__(self):
        return self.category.symbol + ' version ' + str(self.version)

    def statistics(self):
        from django.contrib.auth.models import User
        stats = []
        Item = namedtuple('Item', ['name', 'value', 'url'])
        users = User.objects.all()
        annotated_tokens = 0
        annotated_types = 0
        total_tokens = 0
        total_types = 0
        user_types = defaultdict(int)
        user_errors = defaultdict(int)
        for expansion in self.expansion_set.all():
            annotated = False
            for a in expansion.annotation_set.all():
                user_types[a.user] += 1
                if a.head_correct is False or a.comp_head_correct is False:
                    user_errors[a.user] += 1
                annotated = True
            total_tokens += expansion.count
            total_types += 1
            if annotated:
                annotated_tokens += expansion.count
                annotated_types += 1
        token_coverage = float(annotated_tokens) / total_tokens
        type_coverage = float(annotated_types) / total_types
        item = Item('Type coverage', '%.3f (%d/%d)' % (type_coverage,
            annotated_types, total_types), '')
        stats.append(item)
        item = Item('Token coverage', '%.3f (%d/%d)' % (token_coverage,
            annotated_tokens, total_tokens), '')
        stats.append(item)
        for user in user_types:
            item = Item('Annotations by ' + user.username,
                    '%d' % (user_types[user]), '')
            stats.append(item)
        for user in user_errors:
            url = 'errors/suite-' + str(self.id) + '/user-' + user.username
            item = Item('Errors seen by ' + user.username,
                    '%d' % (user_errors[user]), url)
            stats.append(item)
        return stats


class Expansion(models.Model):
    test_suite = models.ForeignKey('TestSuite')
    rule = models.CharField(max_length=1024)
    supa_example = models.TextField(blank=True)
    penn_example = models.TextField(blank=True)
    index = models.IntegerField()
    count = models.IntegerField()

    def __unicode__(self):
        return str(self.test_suite) + ' exp ' + self.rule

    def supa_example_as_table(self):
        html = '<table>'
        for line in self.supa_example.split('\n'):
            html += '<tr>'
            for field in line.split():
                html += '<td>' + field + '</td>'
            html += '</tr>'
        html += '</table>'
        return html

    def penn_example_rendered(self):
        return self.penn_example.replace(' ', '&nbsp;')

    def head_correct_box(self):
        from django.forms.widgets import NullBooleanSelect
        s = NullBooleanSelect()
        if self.head_correct is None:
            value = '1'
        elif self.head_correct:
            value = '2'
        else:
            value = '3'
        return s.render('expansion-'+str(self.id) + '-head', value)

    def comp_head_correct_box(self):
        from django.forms.widgets import NullBooleanSelect
        s = NullBooleanSelect()
        if self.comp_head_correct is None:
            value = '1'
        elif self.comp_head_correct:
            value = '2'
        else:
            value = '3'
        return s.render('expansion-'+str(self.id) + '-comp', value)


class Annotation(models.Model):
    user = models.ForeignKey('auth.User')
    expansion = models.ForeignKey('Expansion')
    head_correct = models.NullBooleanField()
    comp_head_correct = models.NullBooleanField()
    notes = models.TextField(blank=True)


class Comment(models.Model):
    annotation = models.ForeignKey('Annotation')
    user = models.ForeignKey('auth.User')
    comment = models.TextField()
