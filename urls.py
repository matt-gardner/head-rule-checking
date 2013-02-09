from django.conf.urls.defaults import patterns, include, url
from django.conf import settings

name = '(?P<name>[^/]+)'
suite_id = '(?P<suite_id>\d+)'
username = '(?P<username>[^/]+)'
val = '(?P<val>[^/]+)'

urlpatterns = patterns('',
    url(r'^$',
        'test_suite.views.main'),
    url(r'^suite-'+suite_id+'$',
        'test_suite.views.test_suite'),
    url(r'^errors/suite-'+suite_id+'/user-'+username+'$',
        'test_suite.views.errors'),
    url(r'^ajax/update/'+name+'/'+val+'$', 'test_suite.views.update'),

    # Site media
    (r'^static/(?P<path>.*)$',
        'django.views.static.serve',
        {'document_root': settings.STATIC_ROOT}),

    # Login stuff
    (r'accounts/login/$', 'django.contrib.auth.views.login', {'template_name':
        'login.html'}),
)
