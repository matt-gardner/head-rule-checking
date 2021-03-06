from django.conf.urls import patterns, include, url
from django.conf import settings

annotation_id = '(?P<annotation_id>\d+)'
name = '(?P<name>[^/]+)'
subset = '(?P<subset>[^/]+)'
suite_id = '(?P<suite_id>\d+)'
username = '(?P<username>[^/]+)'
val = '(?P<val>[^/]+)'

urlpatterns = patterns('',
    url(r'^$',
        'test_suite.views.main'),
    url(r'^suite-'+suite_id+'/$',
        'test_suite.views.test_suite'),
    url(r'^suite-'+suite_id+'/'+subset+'$',
        'test_suite.views.test_suite'),
    url(r'^all-annotations/suite-'+suite_id+'$',
        'test_suite.views.all_annotations'),
    url(r'^all-annotations/suite-'+suite_id+'/'+subset+'$',
        'test_suite.views.all_annotations'),
    url(r'^errors/suite-'+suite_id+'/user-'+username+'$',
        'test_suite.views.errors'),
    url(r'^comments/suite-'+suite_id+'/user-'+username+'$',
        'test_suite.views.comments'),
    url(r'^annotations/suite-'+suite_id+'/user-'+username+'$',
        'test_suite.views.annotations'),
    url(r'^unknown/suite-'+suite_id+'/user-'+username+'$',
        'test_suite.views.unknown'),
    url(r'^ajax/update/'+name+'/'+val+'$', 'test_suite.views.update'),
    url(r'^ajax/delete/'+annotation_id+'$',
        'test_suite.views.delete_annotation'),

    # Site media
    (r'^static/(?P<path>.*)$',
        'django.views.static.serve',
        {'document_root': settings.STATIC_ROOT}),

    # Login stuff
    (r'accounts/login/$', 'django.contrib.auth.views.login', {'template_name':
        'login.html'}),
)
