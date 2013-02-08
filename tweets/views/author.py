from django.contrib.auth.decorators import permission_required, login_required
from django.shortcuts import render
from tweets.models import Tweet

@login_required
@permission_required('tweets.is_author', login_url="/tweet_app/author/no_perm/")
# {{{ def index(request):
def index(request):
    user_tweets = Tweet.objects.filter(author=request.user, for_editors=False, twitter_id=None)
    message = ''
    text = ''
    id = None
    if request.POST:
        tweet = None
        text = request.POST.get('tweet')
        action = request.POST.get('action')
        if action == 'publish':
            try:
                id = request.POST.get('id')
                tweet = Tweet.objects.get(id=id)
                tweet.tweet = text
                tweet.save()
                success, error, text = tweet.publish()
                tweet.save()
                if not success:
                    message = 'Your message was not properly authored. Sending to editors.'
            except:
                message = 'There was an error publishing'

        elif action == 'save':
            tweet = Tweet(tweet=text, author=request.user)
            tweet.save()

    data = {'user_tweets': user_tweets, 'message': message, 'text': text, 'id': id }
    return render(request, 'tweets/author/index.html', data)

# }}}
@login_required
def no_perm(request):
    return render(request, 'tweets/author/no_perm.html')
