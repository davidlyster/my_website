from django import forms

# this is the basic search form on the twitter page
class BasicSearchForm(forms.Form):
    search_term = forms.CharField(label='Search...', max_length=100)
    search_amount = forms.IntegerField(label='Num Tweets...', max_value=100)
