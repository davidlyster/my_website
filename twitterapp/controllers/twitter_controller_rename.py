from twitterapp.twitterapp_configs import hidden_config as config
import tweepy as tw

consumer_key = config.consumer_key
consumer_secret = config.consumer_secret
access_token = config.access_token
access_token_secret = config.access_token_secret


class TwitterAPI:

    def __init__(self):
        self.name = 'temp_twitter_api_object'

        # declare api 'object' then authenticate
        # can probably just skip self.api = None but then will authenticate function make new object, api, in class?
        self.api = None
        self.authenticate_api()

    def authenticate_api(self):
        """
        Create and return authenticated twitter API object using my user and project credentials in 'hidden_config' file
        :return:
        """
        # Create the authentication object
        auth = tw.OAuthHandler(consumer_key, consumer_secret)
        # Setting access tokens
        auth.set_access_token(access_token, access_token_secret)
        # Creating the API object while passing in auth information

        self.api = tw.API(auth)

        return

    # should this be @staticmethod??
    def search_term_since_date(self, term, date, tweet_count=10, exclude_retweets=False, text_only=False,
                               full_tweets=False):
        """
        .Cursor() returns an object that you can iterate or loop over to access the data collected.
        Each item in the iterator has various attributes that you can access to get information about each tweet including:
        the text of the tweet, who sent the tweet,the date the tweet was sent and more.
        :param term: search term
        :param date: YYYY-MM-DD date from which the search will take tweets from
        :param tweet_count: amount of tweets to show (10 = 10 most recent)
        :param exclude_retweets: set to true to remove retweets from search results
        :param text_only: do we want text only from tweet or whole tweet json object
        :param full_tweets: if false, the truncated text will returned instead of full 280 chars
        :return: list of tweets
        """

        search_words = term
        if exclude_retweets:
            search = search_words + " -filter:retweets"
        else:
            search = search_words
        date_since = str(date)

        # Collect tweets with Cursor object
        if full_tweets:
            tweets = tw.Cursor(self.api.search, q=search, lang="en", since=date_since, tweet_mode='extended').items(tweet_count)
        else:
            tweets = tw.Cursor(self.api.search, q=search, lang="en", since=date_since).items(tweet_count)

        tweet_list = []

        # Iterate and print tweets
        for tweet in tweets:
            # print(tweet)                                          # the full 'tweet' object
            # print(tweet.text)                                     # just the tweet's text
            # print(tweet.user.screen_name, "Tweeted:", tweet.text)   # username and tweet text
            # print("#########################################################")
            if text_only:
                if full_tweets:
                    tweet_list.append(tweet.full_text)
                else:
                    tweet_list.append(tweet.text)
            else:
                # the tweet object is a 'Status' object with the json within it, use '_json' to retrieve only the json
                tweet_list.append(tweet._json)
            # TODO make sure next line is uncommented unless testing
            # print(tweet)
        return tweet_list

