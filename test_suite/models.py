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
        items = []
        headers = ('User', 'Annotated', 'Errors', 'Comments', 'Unknown',
                'Multiply Annotated')
        rows = []
        Statistics = namedtuple('Statistics', ['items', 'headers', 'rows'])
        Item = namedtuple('Item', ['name', 'value', 'url'])
        Row = namedtuple('Row', ['items'])
        blank_item = Item('', '', '')
        users = User.objects.all()
        annotated_tokens = 0
        annotated_types = 0
        total_tokens = self.expansion_set.aggregate(Sum('count'))['count__sum']
        total_types = self.expansion_set.count()
        user_types = defaultdict(int)
        user_errors = defaultdict(int)
        user_comments = defaultdict(int)
        user_unknown = defaultdict(int)
        annotation_counts = defaultdict(int)
        annotated = set()
        with_errors = set()
        with_comments = set()
        unknown = set()
        for a in Annotation.objects.select_related().filter(
                expansion__test_suite=self):
            annotation_counts[a.expansion_id] += 1
            user_types[a.user] += 1
            if a.head_correct is False or a.comp_head_correct is False:
                user_errors[a.user] += 1
                with_errors.add(a.expansion_id)
            if a.notes:
                user_comments[a.user] += 1
                with_comments.add(a.expansion_id)
            if a.head_correct is None or a.comp_head_correct is None:
                user_unknown[a.user] += 1
                unknown.add(a.expansion_id)
            if a.expansion_id not in annotated:
                annotated_tokens += a.expansion.count
                annotated_types += 1
            annotated.add(a.expansion_id)
        token_coverage = float(annotated_tokens) / total_tokens
        type_coverage = float(annotated_types) / total_types
        if len(annotated) > 0:
            error_percent = float(len(with_errors)) / len(annotated)
        else:
            error_percent = 0
            comment_percent = 0
        item = Item('Type coverage', '%.3f (%d/%d)' % (type_coverage,
            annotated_types, total_types), '')
        items.append(item)
        item = Item('Token coverage', '%.3f (%d/%d)' % (token_coverage,
            annotated_tokens, total_tokens), '')
        items.append(item)
        item = Item('Error rate', '%.3f (%d/%d)' % (error_percent,
            len(with_errors), len(annotated)), '')
        items.append(item)
        users = set(user_types.keys())
        users.union(user_errors.keys())
        users.union(user_comments.keys())
        users.union(user_unknown.keys())
        for user in users:
            row_items = []
            row_items.append(Item('', user.username, ''))
            if user in user_types:
                url = 'annotations/suite-' + str(self.id) + '/user-'
                url += user.username
                row_items.append(Item('', user_types[user], url))
            else:
                row_items.append(blank_item)
            if user in user_errors:
                url = 'errors/suite-' + str(self.id) + '/user-'
                url += user.username
                row_items.append(Item('', user_errors[user], url))
            else:
                row_items.append(blank_item)
            if user in user_comments:
                url = 'comments/suite-' + str(self.id) + '/user-'
                url += user.username
                row_items.append(Item('', user_comments[user], url))
            else:
                row_items.append(blank_item)
            if user in user_unknown:
                url = 'unknown/suite-' + str(self.id) + '/user-'
                url += user.username
                row_items.append(Item('', user_unknown[user], url))
            else:
                row_items.append(blank_item)
            rows.append(Row(row_items))
        row_items = []
        row_items.append(Item('', 'Total', ''))
        url = 'all-annotations/suite-' + str(self.id)
        row_items.append(Item('', len(annotated), url))
        url = 'all-annotations/suite-' + str(self.id) + '/errors'
        row_items.append(Item('', len(with_errors), url))
        url = 'all-annotations/suite-' + str(self.id) + '/comments'
        row_items.append(Item('', len(with_comments), url))
        url = 'all-annotations/suite-' + str(self.id) + '/unknown'
        row_items.append(Item('', len(unknown), url))
        num_multiply_annotated = 0
        for a in annotation_counts:
            if annotation_counts[a] > 1:
                num_multiply_annotated += 1
        url = 'all-annotations/suite-' + str(self.id) + '/multiply-annotated'
        row_items.append(Item('', num_multiply_annotated, url))
        rows.append(Row(row_items))
        return [Statistics(items, headers, rows)]


class Expansion(models.Model):
    test_suite = models.ForeignKey('TestSuite')
    rule = models.CharField(max_length=1024)
    supa_example = models.TextField(blank=True)
    penn_example = models.TextField(blank=True)
    simple_supa_example = models.TextField(blank=True)
    simple_penn_example = models.TextField(blank=True)
    index = models.IntegerField()
    count = models.IntegerField()

    def __unicode__(self):
        return str(self.test_suite) + ' exp ' + self.rule

    def supa_example_as_table(self, simple=False):
        example = self.supa_example
        if simple:
            example = self.simple_supa_example
        html = '<table>'
        for line in example.split('\n'):
            html += '<tr>'
            for field in line.split():
                html += '<td>' + field + '</td>'
            html += '</tr>'
        html += '</table>'
        return html

    def simple_supa_example_as_table(self):
        return self.supa_example_as_table(simple=True)

    def penn_example_rendered(self, simple=False):
        example = self.penn_example
        if simple:
            example = self.simple_penn_example
        return example.replace(' ', '&nbsp;')

    def simple_penn_example_rendered(self):
        return self.penn_example_rendered(simple=True)

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

    def comments(self):
        return self.comment_set.all()

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


class Comment(models.Model):
    annotation = models.ForeignKey('Annotation')
    user = models.ForeignKey('auth.User')
    comment = models.TextField()
