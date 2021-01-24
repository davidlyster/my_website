from django import forms

# simple form to request data for a given stock symbol
class BasicStockSearchForm(forms.Form):
    stock_symbol = forms.CharField(label='Search...', max_length=10)
