from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

from tweets.views import app

urlpatterns = patterns('',
    url(r'^$', 'tweets.views.app.home', name='home'),
    url(r'^tweet_app/', include('tweets.urls')),
    url(r'^accounts/login/$', 'accounts.views.login_user'),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
)
