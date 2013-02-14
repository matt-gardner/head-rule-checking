from django.db.models import Sum
from django.db import models

from collections import defaultdict
from collections import namedtuple

class Category(models.Model):
    symbol = models.CharField(max_length=32)

    def __unicode__(self):
        return self.symbol

    def versions(self):
        return self.testsuite_set.order_by('version').prefetch_related(
                'expansion_set')

    class Meta:
        ordering = ['symbol']


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
        total_tokens = self.expansion_set.aggregate(Sum('count'))['count__sum']
        total_types = self.expansion_set.count()
        user_types = defaultdict(int)
        user_errors = defaultdict(int)
        user_comments = defaultdict(int)
        user_unknown = defaultdict(int)
        annotations_dict = defaultdict(list)
        annotated = set()
        for a in Annotation.objects.select_related().filter(
                expansion__test_suite=self):
            user_types[a.user] += 1
            if a.head_correct is False or a.comp_head_correct is False:
                user_errors[a.user] += 1
            if a.notes:
                user_comments[a.user] += 1
            if a.head_correct is None or a.comp_head_correct is None:
                user_unknown[a.user] += 1
            if a.expansion_id not in annotated:
                annotated_tokens += a.expansion.count
                annotated_types += 1
            annotated.add(a.expansion_id)
        token_coverage = float(annotated_tokens) / total_tokens
        type_coverage = float(annotated_types) / total_types
        item = Item('Type coverage', '%.3f (%d/%d)' % (type_coverage,
            annotated_types, total_types), '')
        stats.append(item)
        item = Item('Token coverage', '%.3f (%d/%d)' % (token_coverage,
            annotated_tokens, total_tokens), '')
        stats.append(item)
        for user in user_types:
            url = 'annotations/suite-' + str(self.id) + '/user-' + user.username
            item = Item('Annotations by ' + user.username,
                    '%d' % (user_types[user]), url)
            stats.append(item)
        for user in user_errors:
            url = 'errors/suite-' + str(self.id) + '/user-' + user.username
            item = Item('Errors seen by ' + user.username,
                    '%d' % (user_errors[user]), url)
            stats.append(item)
        for user in user_comments:
            url = 'comments/suite-' + str(self.id) + '/user-' + user.username
            item = Item('Comments made by ' + user.username,
                    '%d' % (user_comments[user]), url)
            stats.append(item)
        for user in user_unknown:
            url = 'unknown/suite-' + str(self.id) + '/user-' + user.username
            item = Item('Unknown by ' + user.username,
                    '%d' % (user_unknown[user]), url)
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
