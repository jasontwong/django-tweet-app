from django.contrib.auth.decorators import permission_required, login_required
from django.shortcuts import render
from django.db.models import Q
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from tweets.models import Tweet

@login_required
@permission_required('tweets.is_editor', login_url="/tweet_app/editor/no_perm/")
def index(request):
    dirty_tweets = Tweet.objects.filter(twitter_id=None, needs_moderation=True, for_editors=True, moderation_reasons__contains='dirty').order_by('created_date')[:10]
    tweeted_tweets = Tweet.objects.filter(~Q(twitter_id=None)).order_by('-created_date')[:10]
    data = { 'dirty': dirty_tweets, 'tweeted': tweeted_tweets }
    return render(request, 'tweets/editor/index.html', data)

@login_required
@permission_required('tweets.is_editor', login_url="/tweet_app/editor/no_perm/")
# {{{ def listing(request, type):
def listing(request, type):
    data = {}
    if type == 'dirty':
        dirty_tweets = Tweet.objects.filter(twitter_id=None, needs_moderation=True, for_editors=True, moderation_reasons__contains='dirty').order_by('created_date')
        paginator = Paginator(dirty_tweets, 10)
        data['has_detail'] = True
        data['title'] = 'Dirty Tweets'

    elif type == 'tweeted':
        tweeted_tweets = Tweet.objects.filter(~Q(twitter_id=None)).order_by('-created_date')[:10]
        paginator = Paginator(tweeted_tweets, 10)
        data['has_detail'] = False
        data['title'] = 'Tweeted Tweets'

    else:
        return redirect('/tweet_app/editor/')

    page = request.GET.get('page')
    try:
        tweets = paginator.page(page)

    except PageNotAnInteger:
        tweets = paginator.page(1)

    except EmptyPage:
        tweets =  paginator.page(paginator.num_pages)

    data['tweets'] = tweets
    return render(request, 'tweets/editor/listing.html', data)

# }}}
@login_required
def no_perm(request):
    return render(request, 'tweets/editor/no_perm.html')
