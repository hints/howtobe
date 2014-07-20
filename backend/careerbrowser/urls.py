from django.conf.urls import patterns, include, url
from django.contrib import admin
admin.autodiscover()


urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'careerbrowser.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^$', 'careerbrowser_core.views.home'),
    url(r'^home/$', 'careerbrowser_core.views.home2'),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^api/', 'careerbrowser_core.views.api_handler')
)
