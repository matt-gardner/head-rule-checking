from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Count
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.shortcuts import render_to_response
from django.template import RequestContext

from test_suite.models import *


def main(request):
    context = RequestContext(request)
    context['categories'] = Category.objects.all()
    return render_to_response('main.html', context)


@login_required
def test_suite(request, suite_id, subset=None):
    context = RequestContext(request)
    suite = get_object_or_404(TestSuite, pk=suite_id)
    context['expansions'] = suite.expansion_set.all()
    page_num = 1
    prev_page = None
    if subset == 'unannotated':
        context['expansions'] = context['expansions'].filter(annotation=None)
    elif subset == 'unannotated-by-me':
        context['expansions'] = context['expansions'].exclude(
                annotation__user=request.user)
    elif subset and 'page' in subset:
        page_num = int(subset.split('-')[-1])
        prev_page = page_num - 1
        if prev_page == 0:
            prev_page = None
    max_expansions = 200
    count = context['expansions'].count()
    if count > max_expansions:
        context['truncated'] = True
        context['num_pages'] = range(1, count / max_expansions + 2)
        context['current_page'] = page_num
        start = (page_num - 1) * max_expansions
        end = start + max_expansions
        context['expansions'] = context['expansions'][start:end]
    for expansion in context['expansions']:
        try:
            annotation = expansion.annotation_set.get(user=request.user)
            expansion.head_correct = annotation.head_correct
            expansion.comp_head_correct = annotation.comp_head_correct
            expansion.notes = annotation.notes
        except Annotation.DoesNotExist:
            expansion.head_correct = None
            expansion.comp_head_correct = None
            expansion.notes = ''
    return render_to_response('test_suite.html', context)


@login_required
def all_annotations(request, suite_id, subset=None):
    context = RequestContext(request)
    suite = get_object_or_404(TestSuite, pk=suite_id)
    context['expansions'] = suite.expansion_set.exclude(annotation=None)
    if subset == 'errors':
        context['expansions'] = context['expansions'].filter(
                Q(annotation__head_correct=False) |
                Q(annotation__comp_head_correct=False))
    elif subset == 'comments':
        context['expansions'] = context['expansions'].exclude(
                annotation__notes="")
    elif subset == 'unknown':
        context['expansions'] = context['expansions'].filter(
            Q(annotation__head_correct__isnull=True) |
            Q(annotation__comp_head_correct__isnull=True))
    elif subset == 'multiply-annotated':
        context['expansions'] = context['expansions'].annotate(
                annotation_count=Count('annotation')).filter(
                        annotation_count__gte=2)
    for expansion in context['expansions']:
        expansion.annotations = []
        for annotation in expansion.annotation_set.all():
            expansion.annotations.append(annotation)
    return render_to_response('all_annotations.html', context)


def errors(request, suite_id, username):
    user = get_object_or_404(User, username=username)
    suite = get_object_or_404(TestSuite, pk=suite_id)
    errors = user.annotation_set.filter(
            Q(expansion__test_suite=suite, head_correct=False) |
            Q(expansion__test_suite=suite, comp_head_correct=False))
    return testsuite_subset(request, suite_id, user, errors)


def comments(request, suite_id, username):
    user = get_object_or_404(User, username=username)
    suite = get_object_or_404(TestSuite, pk=suite_id)
    comments = user.annotation_set.filter(
            expansion__test_suite=suite).exclude(notes="")
    return testsuite_subset(request, suite_id, user, comments)


def annotations(request, suite_id, username):
    user = get_object_or_404(User, username=username)
    suite = get_object_or_404(TestSuite, pk=suite_id)
    annotations = user.annotation_set.filter(expansion__test_suite=suite)
    return testsuite_subset(request, suite_id, user, annotations)


def unknown(request, suite_id, username):
    user = get_object_or_404(User, username=username)
    suite = get_object_or_404(TestSuite, pk=suite_id)
    annotations = user.annotation_set.filter(
            Q(expansion__test_suite=suite, head_correct__isnull=True) |
            Q(expansion__test_suite=suite, comp_head_correct__isnull=True))
    return testsuite_subset(request, suite_id, user, annotations)


@login_required
def testsuite_subset(request, suite_id, user, annotations):
    context = RequestContext(request)
    context['expansions'] = []
    context['username'] = user.username
    context['viewer_username'] = request.user.username
    context['disable'] = user != request.user
    for annotation in annotations:
        expansion = annotation.expansion
        expansion.head_correct = annotation.head_correct
        expansion.comp_head_correct = annotation.comp_head_correct
        expansion.notes = annotation.notes
        expansion.annotation = annotation
        context['expansions'].append(expansion)
    return render_to_response('test_suite.html', context)


@login_required
def update(request, name, val):
    user = request.user
    fields = name.split('-')
    if len(fields) == 3:
        _, id, type = fields
    else:
        return _update_comment(request, fields, val)
    expansion = get_object_or_404(Expansion, pk=id)
    if val == '1':
        correct = None
    elif val == '2':
        correct = True
    elif val == '3':
        correct = False
    try:
        annotation = Annotation.objects.get(expansion=expansion, user=user)
    except Annotation.DoesNotExist:
        annotation = Annotation(expansion=expansion, user=user)
        annotation.save()
    if type == 'head':
        annotation.head_correct = correct
        annotation.save()
    elif type == 'comp':
        annotation.comp_head_correct = correct
        annotation.save()
    elif type == 'notes':
        # The javascript adds quotes around the value, so that you can tell
        # when something was made empty.
        annotation.notes = request.GET['value'][1:-1]
        annotation.save()
    return HttpResponse('')


@login_required
def _update_comment(request, fields, val):
    type, id, __, username, _ = fields
    user = get_object_or_404(User, username=username)
    # The javascript adds quotes around the value, so that you can tell when
    # something was made empty.
    val = val[1:-1]
    response = ''
    if type == 'expansion':
        # This is a new comment
        expansion = get_object_or_404(Expansion, pk=id)
        annotation = get_object_or_404(Annotation, expansion=expansion,
                user=user)
        comment = Comment(user=request.user, annotation=annotation)
        comment.comment = val
        comment.save()
        response = 'comment-%d-user-%s-comment' % (comment.id, username)
    elif type == 'comment':
        comment = get_object_or_404(Comment, user=request.user, pk=id)
        if val:
            comment.comment = val
            comment.save()
            response = 'comment-%d-user-%s-comment' % (comment.id, username)
        else:
            comment.delete()
            response = 'expansion-%s-user-%s-comment' % (id, username)
    return HttpResponse(response)
