from django.conf.urls.defaults import patterns, url


urlpatterns = patterns('inlinetrans.views',
    url(r'^apply_changes/$', 'do_restart', name='apply_changes'),
    url(r'^set_new_translation/$', 'set_new_translation', name='set_new_translation'),
    url(r'^demo/$', 'inline_demo', name='inline_demo'),
)
