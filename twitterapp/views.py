from django.shortcuts import render
from .controllers.twitter_controller_rename import TwitterAPI
from django.http import HttpResponseRedirect
from .Forms import BasicSearchForm
from dev_config import TESTING


def twitter_main(request):
    """
    This is the function to load the main twitter app page
    """

    # TODO: these 2 lines are manual tests, will be removed - this is where the twitter app will start (for now)
    search_term = 'NFL'
    tweet_amount = 10

    twit_api = create_twitter_api_object()

    if request.method == 'POST':
        form = BasicSearchForm(request.POST)

        # check whether it's valid:
        if form.is_valid():
            search_term = form.cleaned_data['search_term']
            tweet_amount = form.cleaned_data['search_amount']
        else:
            # TODO what to do here if error?
            print('not')

    else:
        form = BasicSearchForm()

    # Boolean Values: exclude_retweets, text_only, full_tweets
    tweets_data = twit_api.search_term_since_date(search_term, '2020-11-26', tweet_amount, True, False, True)

    full_tweet_data = extract_specific_tweet_data(tweets_data)

    # this is the set of data that will be passed to the webpage/template
    context = {
        'name': 'twittstuff',
        'search_term': search_term,
        'form': form,
        'full_tweet_data': full_tweet_data,
        'tweet_amount': tweet_amount,
    }

    if TESTING:
        return render(request, 'twitterapp_testing.html', context)
    else:
        return render(request, 'twitterapp_main.html', context)


def extract_specific_tweet_data(tweet_data):
    """
    extract the intended data from a set of tweets and return them as a list of dicts
    :param tweet_data: this should be a list of json formatted tweet data
    """

    final_data = []

    for tw in tweet_data:
        temp_dict = {
            'text': tw['full_text'],
            'author_twitter_name': '@' + str(tw['user']['screen_name']),
            'author_display_name': tw['user']['name'],
            'timestamp': clean_timestamp(tw['created_at']),
            'retweets': tw['retweet_count'],
            'favorites': tw['favorite_count'],
            # this url will be the link to the actual tweet on twitter
            'url': 'https://twitter.com/anyuser/statuses/' + str(tw['id'])
        }

        final_data.append(temp_dict)

    return final_data


def clean_timestamp(timestamp, format=False):
    """
    used to remove unwanted characters from the overly long timestamp in the json data of a tweet
    eg: timestamp comes in as 'Thu Dec 17 13:44:24 +0000 2020' and for now we only want 'Thu Dec 17 13:44'
    """

    cleaned_timestamp_list = str(timestamp).split(' ')[0:4]

    # remove the seconds from the actual time part of the string
    cleaned_timestamp_list[3] = cleaned_timestamp_list[3][0:5]

    # join them back into a string
    cleaned_timestamp = ' '.join(cleaned_timestamp_list)

    return cleaned_timestamp


def create_twitter_api_object():
    """
    call the function in the twitter_controller to instantiate the twitter API
    """
    return TwitterAPI()

