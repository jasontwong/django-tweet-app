from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from constance import config
from twython import Twython, TwythonError, TwythonRateLimitError, TwythonAuthError
from datetime import datetime
from pytz import timezone

# {{{ class Tweet(models.Model):
class Tweet(models.Model):
    tweet = models.CharField(max_length=140)
    author = models.ForeignKey(User, on_delete=models.PROTECT, related_name='author')
    editor = models.ForeignKey(User, null=True, default=None, on_delete=models.PROTECT, related_name='editor')
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)
    moderation_date = models.DateTimeField('when it got caught in moderation filter', blank=True, null=True, default=None)
    published_date = models.DateTimeField('when it was posted to twitter', blank=True, null=True, default=None)
    needs_moderation = models.BooleanField(default=True)
    for_editors = models.BooleanField(default=False)
    moderation_reasons = models.TextField(blank=True, default='')
    retweet_count = models.PositiveIntegerField(default=0)
    twitter_id = models.CharField(max_length=200, null=True, default=None)

    # {{{ def __unicode__(self):
    def __unicode__(self):
        return self.tweet

    # }}}
    # {{{ def has_dirty_words(self):
    def has_dirty_words(self):
        ''' Returns a boolean '''
        is_dirty = False
        words = config.TWEETS_DIRTY_WORDS.lower().split("\r\n")
        text = self.tweet.lower().replace('-', '').replace('_', '')
        for word in words:
            if len(word) > 0:
                is_dirty = text.find(word) != -1
            if is_dirty:
                break

        return is_dirty, 'dirty'

    # }}}
    # {{{ def has_word_all_capitals(self):
    def has_word_all_capitals(self):
        ''' Returns a boolean '''
        is_capital = False
        words = self.tweet.split(' ')
        for word in words:
            is_capital = word.isupper()
            if is_capital:
                break

        return is_capital, 'capitals'

    # }}}
    # {{{ def should_we_moderate(self):
    def should_we_moderate(self):
        reasons = []
        checks = ['has_dirty_words', 'has_word_all_capitals']
        for check in checks:
            should_moderate, reason = getattr(self, check)()
            if should_moderate:
                reasons.append(reason)

        should_moderate = len(reasons) > 0

        return should_moderate, reasons

    # }}}
    # {{{ def rebrand_tweet(self, corrections=None):
    def rebrand_tweet(self, corrections=None):
        text = self.tweet
        if corrections == None:
            fixes = Correction.objects.all()
        else:
            fixes = Correction.objects.filter(proper__in=corrections)
        
        for word in fixes:
            text = word.fix(text)

        return text

    # }}}
    # {{{ def get_live_retweets(self):
    def get_live_retweets(self):
        error = None
        if self.twitter_id != None:
            try:
                tw_api = Twython(app_key=config.TWITTER_API_KEY,
                                app_secret=config.TWITTER_API_SECRET,
                                oauth_token=config.TWITTER_OAUTH_TOKEN,
                                oauth_token_secret=config.TWITTER_OAUTH_SECRET)
                retweets = tw_api.getRetweets(id=self.twitter_id)
                self.retweet_count = len(retweets)

            except:
                # pass error information would be better
                error = 'api error'
        else:
            error = 'tweet has no twitter_id'

        return self.retweet_count, error

    # }}}
    # {{{ def publish(self):
    def publish(self):
        success = False
        error = None
        text = self.tweet
        if self.twitter_id == None:
            text = self.rebrand_tweet()
            if text == self.tweet:
                moderate, reasons = self.should_we_moderate()
                if not moderate:
                    try:
                        tw_api = Twython(app_key=config.TWITTER_API_KEY,
                                        app_secret=config.TWITTER_API_SECRET,
                                        oauth_token=config.TWITTER_OAUTH_TOKEN,
                                        oauth_token_secret=config.TWITTER_OAUTH_SECRET)
                        tweet = tw_api.updateStatus(status=self.tweet)
                        self.twitter_id = tweet['id_str']
                        self.needs_moderation = False
                        self.published_date = datetime.now(timezone(settings.TIME_ZONE))
                        success = True

                    except (TwythonError, TwythonRateLimitError, TwythonAuthError):
                        # pass error information would be better
                        error = 'api error'

                    except:
                        error = 'some other error'

                else:
                    error = 'needs moderation'
                    if self.moderation_date == None:
                        self.moderation_date = datetime.now(timezone(settings.TIME_ZONE))

                    self.moderation_reasons = "\n".join(reasons)

            else:
                error = 'tweet needs to be changed for branding'
        
            if error != None:
                self.for_editors = True

        else:
            error = 'This is already published'

        return success, error, text

    # }}}

    # {{{ class Meta:
    class Meta:
        permissions = {
            ('is_author', 'Has author privs'),
            ('is_editor', 'Has editor privs'),
        }

    # }}}
# }}}
# {{{ class Correction(models.Model):
class Correction(models.Model):
    proper = models.CharField('what the text should be', max_length=200, unique=True)
    # there were no good array field modules that are cross-platform
    improper = models.TextField('misspellings separated by new lines')

    # {{{ def __unicode__(self):
    def __unicode__(self):
        return self.proper

    # }}}
    # {{{ def fix(self, text):
    def fix(self, text):
        words = self.improper.split("\r\n")
        for word in words:
            text = text.replace(word, self.proper)

        return text

    # }}}
# }}}
