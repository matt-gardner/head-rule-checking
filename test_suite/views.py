from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
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
def test_suite(request, suite_id):
    context = RequestContext(request)
    suite = get_object_or_404(TestSuite, pk=suite_id)
    context['expansions'] = suite.expansion_set.all()
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


def errors(request, suite_id, username):
    context = RequestContext(request)
    user = get_object_or_404(User, username=username)
    suite = get_object_or_404(TestSuite, pk=suite_id)
    context['expansions'] = []
    context['disable'] = True
    errors = user.annotation_set.filter(
            Q(expansion__test_suite=suite, head_correct=False) |
            Q(expansion__test_suite=suite, comp_head_correct=False))
    for error in errors:
        expansion = error.expansion
        expansion.head_correct = error.head_correct
        expansion.comp_head_correct = error.comp_head_correct
        expansion.notes = error.notes
        context['expansions'].append(expansion)
    return render_to_response('test_suite.html', context)


@login_required
def update(request, name, val):
    user = request.user
    _, id, type = name.split('-')
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
        annotation.notes = request.GET['value']
        annotation.save()
    return HttpResponse('')
