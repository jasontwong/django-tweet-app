from django.conf.urls import patterns, url

from tweets.views import app, author, editor

urlpatterns = patterns('',
    url(r'^$', app.index),
    url(r'^detail/(?P<tweet_id>\d+)/$', app.detail),
    url(r'^ajax/moderate/$', app.moderate),
    url(r'^ajax/save/$', app.save),
    url(r'^ajax/publish/$', app.publish),
    url(r'^ajax/get-live-retweets/$', app.get_live_retweets),
    url(r'^ajax/shorten-url/$', app.shorten_url),

    url(r'^author/$', author.index),
    url(r'^author/no_perm/$', author.no_perm),

    url(r'^editor/$', editor.index),
    url(r'^editor/no_perm/$', editor.no_perm),
    url(r'^editor/listing/(?P<type>\w+)/$', editor.listing),
)
