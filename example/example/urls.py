try:
    from django.conf.urls import include, patterns, url
except ImportError:  # Django < 1.5
    from django.conf.urls.defaults import include, patterns, url

from django.contrib import admin
from django.views.generic import TemplateView


admin.autodiscover()

js_info_dict = {
    'packages': ('django.conf',),
}

URL_SEND_EMAIL = '/admin/send-email/'

urlpatterns = patterns('',
    url(r'^jsi18n/$', 'django.views.i18n.javascript_catalog', js_info_dict),
    url(r'^$', TemplateView.as_view(template_name='app/index.html'), name='index'),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^inlinetrans/', include('inlinetrans.urls')),
)
