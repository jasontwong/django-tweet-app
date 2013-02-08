from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.http import HttpResponse
from tweets.models import Tweet
from constance import config
import json, bitly_api

def index(request):
    return render(request, 'tweets/index.html')

def home(request):
    return render(request, 'tweets/home.html')

@login_required
# {{{ def detail(request, tweet_id):
def detail(request, tweet_id):
    tweet = None
    message = ''
    user = request.user
    is_author = user.has_perm('tweets.is_author')
    is_editor = user.has_perm('tweets.is_editor')
    if request.POST and (is_author or is_editor):
        tweet_id = request.POST.get('id')
        tweet = Tweet.objects.get(id=tweet_id)
        tweet.tweet = request.POST.get('tweet')
        tweet.save()
        action = request.POST.get('action')
        message = 'saved'
        if action == 'publish':
            tweet.publish()
            tweet.save()
            if is_author:
                return redirect('/tweet_app/author/')

            if is_editor:
                return redirect('/tweet_app/editor/')

    template = tpl_no_access = 'tweets/no_access.html'
    tpl_detail = 'tweets/detail.html'
    if tweet == None:
        try:
            if is_author:
                tweet = Tweet.objects.get(id=tweet_id, author=user)
                template = tpl_detail

            if is_editor and template != tpl_detail:
                tweet = Tweet.objects.get(id=tweet_id, for_editors=True, twitter_id=None)
                template = tpl_detail

        except:
            template = tpl_no_access

    else:
        template = tpl_detail

    data = { 'tweet': tweet, 'is_author': is_author, 'is_editor': is_editor, 'message': message }
    return render(request, template, data)

# }}}
@login_required
# {{{ def moderate(request):
def moderate(request):
    data = {}
    data['error'] = None
    data['moderate'] = False
    data['reasons'] = []
    try:
        if request.POST:
            id = request.POST.get('id')
            text = request.POST.get('tweet')
            user = request.user
            if len(id) > 0:
                tweet = Tweet.objects.get(id=id)
                tweet.tweet = text
                tweet.editor = user

            else:
                tweet = Tweet(tweet=text, author=user)

            moderate, reasons = tweet.should_we_moderate()
            if not moderate or len(id) > 0:
                tweet.save()

            data['id'] = tweet.id
            data['moderate'] = moderate
            data['reasons'] = reasons

        else:
            data['error'] = "How'd you get here? This is an ajax call"

    except:
        data['error'] = 'There was an error'

    return HttpResponse(json.dumps(data), content_type='application/json')

# }}}
@login_required
# {{{ def publish(request):
def publish(request):
    data = {}
    data['success'] = False
    data['error'] = None
    data['uri'] = '/accounts/login/'
    try:
        if request.POST:
            id = request.POST.get('id')
            user = request.user
            tweet = Tweet.objects.get(id=id)
            data['success'], data['error'], data['text'] = tweet.publish()
            tweet.save()

            if user.has_perm('tweets.is_author'):
                data['uri'] = '/tweet_app/author/'

            elif user.has_perm('tweets.is_editor'):
                data['uri'] = '/tweet_app/editor/'

        else:
            data['error'] = "How'd you get here? This is an ajax call"

    except:
        data['error'] = 'There was an error'

    return HttpResponse(json.dumps(data), content_type='application/json')

# }}}
@login_required
# {{{ def save(request):
def save(request):
    data = {}
    data['success'] = False
    data['error'] = None
    data['uri'] = '/accounts/login/'
    try:
        if request.POST:
            id = request.POST.get('id')
            text = request.POST.get('tweet')
            user = request.user
            if len(id) > 0:
                tweet = Tweet.objects.get(id=id)
                tweet.editor = user

            else:
                tweet = Tweet(tweet=text, author=user)

            tweet.save()
            data['success'] = True
            if user.has_perm('tweets.is_author'):
                data['uri'] = '/tweet_app/author/'

            elif user.has_perm('tweets.is_editor'):
                data['uri'] = '/tweet_app/editor/'

        else:
            data['error'] = "How'd you get here? This is an ajax call"

    except:
        data['error'] = 'There was an error'

    return HttpResponse(json.dumps(data), content_type='application/json')

# }}}
@login_required
# {{{ def get_live_retweets(request):
def get_live_retweets(request):
    data = {}
    data['success'] = False
    data['error'] = None
    data['count'] = -1
    try:
        if request.POST:
            id = request.POST.get('id')
            tweet = Tweet.objects.get(id=id)
            data['count'], data['error'] = tweet.get_live_retweets()
            if data['error'] == None:
                tweet.save()
                data['success'] = True

        else:
            data['error'] = "How'd you get here? This is an ajax call"

    except:
        data['error'] = 'There was an error'

    return HttpResponse(json.dumps(data), content_type='application/json')

# }}}
@login_required
# {{{ def shorten_url(request):
def shorten_url(request):
    data = {}
    data['success'] = False
    data['error'] = None
    data['url'] = ''
    try:
        if request.POST:
            url = request.POST.get('url')
            bitly = bitly_api.Connection(access_token=config.BITLY_ACCESS_TOKEN)
            info = bitly.shorten(url)
            data['url'] = info['url']
            data['success'] = True

        else:
            data['error'] = "How'd you get here? This is an ajax call"

    except:
        data['error'] = 'There was an error'

    return HttpResponse(json.dumps(data), content_type='application/json')

# }}}
