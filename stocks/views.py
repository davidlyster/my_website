from django.shortcuts import render
from dev_config import TESTING
import pandas as pd
import numpy as np
import datetime
import yfinance as yf   # Yahoo! Finance market data downloader
from pandas_datareader import data as pdr
import json
from .Forms import BasicStockSearchForm

"""
TODO
- make one var for timestamp_to_date(date) so function only called once
- clean up code with subfunctions
- look into yfinance and pdr
- decide on defualt stock ticker (if there even should be one?)
"""

def stocks_main(request):

    # this is just the default and is replaced when a post request is received
    stock_ticker="ETH-USD"

    if request.method == 'POST':
        form = BasicStockSearchForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            stock_ticker = form.cleaned_data['stock_symbol']
        else:
            # TODO what to do here if error?
            print('not')
    else:
        form = BasicStockSearchForm()

    ticker, logs, rbws, dates, closing_prices = analyse_stock_and_retrieve_date(stock_ticker)

    context = {
        'stocksstuff': None,
        'stock_ticker': ticker,
        'stock_analysis_logs': logs,
        'stock_rbw_statements': rbws,
        'dates': json.dumps(dates),
        'closing_prices': closing_prices,
        # get min & max values +/- 10% to set graph values range
        'min': min(closing_prices)*0.9,
        'max': max(closing_prices)*1.1
    }

    if TESTING:
        return render(request, 'stockshome_testing.html', context)
    else:
        return render(request, 'stockshome.html', context)


def analyse_stock_and_retrieve_date(stock_ticker="ETH-USD"):
    """
    base (version 1) function to do analysis on a stock symbol
    return: stock ticker (eg.TSLA, BTC-USD), statements about analysis on the stock and graphing data

    eg stocks:
    TSLA    - tesla
    BTC-USD - bitcoin
    ETH-USD - ethereum
    LTC-USD - litecoin
    """

    # declare list of analysis statements to be returned
    analysis = []       # this is basically just logs  
    red_blue_white = [] # this'll be a tracker for the RBW graph log per adj close
    dates = []          # dates for the graph 
    closing_prices = [] # prices for the graph

    # apparently activates a workaround needed to get around yahoos updated way of accessing their stock data
    yf.pdr_override()

    analysis.append("{0} Selected".format(stock_ticker))

    # TODO: allow user to pass in date range?
    #  if so, make sure date is ocrrect format
    start_date = datetime.date(2020, 7, 6)  # YYYY-MM-DD

    # get current date/time
    now = datetime.datetime.now()

    # get stock data within timeframe and store in pandas DataFrame
    df = pdr.get_data_yahoo(stock_ticker, start_date, now)

    # values in emasUsed are the amount of datapoints observed in the EMA calculation
    emasUsed = [3, 5, 8, 10, 12, 15, 30, 35, 40, 45, 50, 60]

    # make a column in our dataframe for each ema calculation
    for datapoints_count in emasUsed:
        df["Ema_{0}".format(datapoints_count)] = round(df.iloc[:,4].ewm(span=datapoints_count, adjust=False).mean(),2)

    # show more columns if needed
    # pd.set_option('display.max_columns', 500)
    # print(df)

    # NEXT: iterate through all dates and make calculations and findings
    # CALCULATIONS:
    # cmin and cmax: min value of short (3-15) emas, max of long (30-60)
    # TODO what exactly is RED or BLUE

    in_position = False  # position is True when we have bought a stock
    num = 0
    bp = 0       # buy price, set a time of buying/setting a position
    sp = 0       # sell price
    percentage_change = []

    # IMPORTANT - this loop is where we define our strategy
    # replace the code in here to try out different methods
    for date in df.index:   # date is the index of our dataframe

        # Ema_x: column names given in line 44
        cmin = min(df["Ema_3"][date], df["Ema_5"][date], df["Ema_8"][date],
                df["Ema_10"][date], df["Ema_12"][date], df["Ema_15"][date])

        cmax = min(df["Ema_30"][date], df["Ema_35"][date], df["Ema_40"][date],
                df["Ema_45"][date], df["Ema_50"][date], df["Ema_60"][date])

        # get the close (adjusted) value for the date too
        close = df["Adj Close"][date]

        # populate arrays used to define line graph
        dates.append(timestamp_to_date(date, True))
        closing_prices.append(round(close,3))

        if cmin > cmax:
            # opening position
            print("{0} RED WHITE BLUE".format(timestamp_to_date(date)))
            red_blue_white.append(["info", "{0} RED WHITE BLUE".format(timestamp_to_date(date))])

            # make the buy if we currently do not hold a position
            if not in_position:
                bp = close
                in_position = True
                print("{0}: Buying now @ {1}".format(bp, timestamp_to_date(date)))
                analysis.append("{0}: Buying now @ {1}".format(round(bp,3), timestamp_to_date(date)))
                red_blue_white.append(["alert", "{0}: Buying now @ {1}".format(round(bp,3), timestamp_to_date(date))])

        elif cmin < cmax:
            # closing position
            print("{0} BLUE WHITE RED".format(timestamp_to_date(date)))
            red_blue_white.append(["info", "{0} BLUE WHITE RED".format(timestamp_to_date(date))])

            # sell if we are in positiont
            if in_position:
                # do the sale
                sp = close
                in_position = False
                print("{0}: Selling now @ {1}".format(sp, timestamp_to_date(date)))
                analysis.append("{0}: Selling now @ {1}".format(round(sp,3), timestamp_to_date(date)))
                red_blue_white.append(["alert", "{0}: Selling now @ {1}".format(round(sp,3), timestamp_to_date(date))])
                # calculate % change in price then store in our list of trades/trade evaluations
                pc = (sp/bp-1)*100
                percentage_change.append(round(pc,3))

        # check if we still have open position at end of dataframe
        num += 1
        if num == df["Adj Close"].count() and in_position:
            # NOTE: repeated code should be put in func instead but not bothered atm
            # close position
            sp = close
            in_position = False
            print("{0}(FINAL): Selling now @ {1}".format(sp, timestamp_to_date(date)))
            analysis.append("{0}(FINAL): Selling now @ {1}".format(round(sp,3), timestamp_to_date(date)))
            red_blue_white.append(["alert", "{0}(FINAL): Selling now @ {1}".format(round(sp,3), timestamp_to_date(date))])
            # calculate % change in price then store in our list of trades/trade evaluations
            pc = (sp / bp - 1) * 100
            percentage_change.append(round(pc,3))

    # print(percentage_change)
    analysis.append("Trade Return Percentages\n"+str(percentage_change))

    # NEXT: make calculations to analyse strategy
    # declare vars for values we will calculate
    gains = 0
    num_gains = 0
    losses = 0
    num_losses = 0
    total_return = 1
    average_gain = 0
    average_loss = 0
    # these will be replaced if we have any gains/losses respectively
    max_return = "undefined"
    max_loss = "undefined"
    gainloss_ratio = 'inf'
    hit_ratio = 0

    # for each percentage_change, i.e. outcome of each trade
    # record gains/losses and aggregate final return
    for trade in percentage_change:
        if trade > 0:
            # if we made a gain on the trade
            gains += trade
            num_gains += 1
        else:
            # if we did not gain
            losses += trade
            num_losses += 1
        # eg: +7% trade: multiply by 1.07 (7/100 + 1)
        total_return = total_return * ((trade/100)+1)

    # -1: remove the initial 1 for total_return
    total_return = round((total_return-1)*100, 2)

    # calculate average gains/losses, max gain/loss and gainloss_ratio
    if num_gains > 0:
        average_gain = gains/num_gains
        max_return = max(percentage_change)

    if num_losses > 0:
        average_loss = losses/num_losses
        max_loss = min(percentage_change)
        gainloss_ratio = (-average_gain/average_loss)

    # calculate hit ratio, how often trade was a gain
    if num_gains > 0 or num_losses > 0:
        hit_ratio = num_gains/(num_losses+num_gains)

    # likely to not need these prints but keeping for now just in case
    # Display Analysis
    # print()
    # print("Results for "+stock_ticker+" going back to "+str(df.index[0])+", Sample size: "+str(num_gains+num_losses)+" trades")
    # print("EMAs used: "+str(emasUsed))
    # print("Hit Ratio: "+ str(hit_ratio))
    # print("Gain/loss ratio: "+str(gainloss_ratio))
    # print("Average Gain: "+str(average_gain))
    # print("Average Loss: "+str(average_loss))
    # print("Max Return: "+str(max_return))
    # print("Max Loss: "+str(max_loss))
    # print("Total return over "+str(num_gains+num_losses)+" trades: "+str(total_return)+"%")
    # print("Example return Simulating "+str(n)+ " trades: "+ str(nReturn)+"%" )
    # print()

    # add all of these statements to a list to be displayed on screen
    analysis.append("Results for "+stock_ticker+" going back to "+str(df.index[0])+", Sample size: "+str(num_gains+num_losses)+" trades")
    analysis.append("EMAs used: "+str(emasUsed))
    analysis.append("Hit Ratio: "+ str(round(hit_ratio, 2)))
    analysis.append("Gain/loss ratio: "+str(round(gainloss_ratio,2)))
    analysis.append("Average Gain: "+str(round(average_gain,2)))
    analysis.append("Average Loss: "+str(round(average_loss)))
    analysis.append("Max Return: "+str(max_return))
    analysis.append("Max Loss: "+str(max_loss))
    analysis.append("Total return over "+str(num_gains+num_losses)+" trades: "+str(total_return)+"%")

    return stock_ticker, analysis, red_blue_white, dates, closing_prices


def timestamp_to_date(timestamp, return_as_string=False):
    # turn pandas timestamp into YYYY-MM-DD format
    if return_as_string:
        return str(timestamp.strftime('%Y-%m-%d'))
    return timestamp.date()
