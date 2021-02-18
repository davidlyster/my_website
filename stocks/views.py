from django.shortcuts import render
from dev_config import TESTING
import pandas as pd
import numpy as np
import datetime
import yfinance as yf   # Yahoo! Finance market data downloader
from pandas_datareader import data as pdr
import json
from .Forms import BasicStockSearchForm
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required

"""
TODO
- what should default stock_ticker be? or should there be a page beforehand with suggestions?
- look into yfinance and pdr
- what to do if "form.is_valid()" returns false? is it even possible?
- custom date range for stock lookup?
"""

@csrf_exempt
# @login_required(login_url="/login/")
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

    # clearer names in the context{} below
    ticker, logs, red_blue_white_log, dates, closing_prices, rwb_bool, null_return = analyse_stock_and_retrieve_date(stock_ticker)

    if null_return:
        return render(request, 'stockshome_invalid_symbol.html', context={'stock_ticker': ticker})

    current_position = "Buy" if rwb_bool else "Sell"

    context = {
        'stock_ticker': ticker,
        'stock_analysis_logs': logs,
        'red_blue_white_log': red_blue_white_log,
        # 'stock_rbw_statements': rbws,
        'dates': json.dumps(dates),
        'closing_prices': closing_prices,
        # get min & max values +/- 10% to set graph values range
        'min': min(closing_prices)*0.9,
        'max': max(closing_prices)*1.1,
        'current_position': current_position,
        'current_price': round(closing_prices[-1],2)
    }

    if TESTING:
        return render(request, 'stockshome_testing.html', context)
    else:
        return render(request, 'stockshome.html', context)


def analyse_stock_and_retrieve_date(stock_ticker="ETH-USD"):
    """
    (version 1) function to do analysis on a stock symbol and return logs and graph data for the front end
    return: stock ticker (eg.TSLA, BTC-USD), statements about analysis on the stock and graphing data
    
    Trading Algorithm
    Simple enough formula based on using RED/BLUE/WHITE anlaysis where...
    RED:    corresponds to the minimum exponential moving average (ema) value among the selected short emas (3, 5, 8, 10, 12, 15)
    WHITE:  closing adjusted stock price
    BLUE:   corresponds to the maximum exponential moving average (ema) value among the selected long emas (30, 35, 40, 45, 50, 60)

    eg stocks:
    TSLA    - tesla
    BTC-USD - bitcoin
    ETH-USD - ethereum
    LTC-USD - litecoin
    XRP-USD - ripple
    """

    # apparently activates a workaround needed to get around yahoos updated way of accessing their stock data
    yf.pdr_override()

    # TODO: allow user to pass in date range?
    # if so, make sure date is correct format
    start_date = datetime.date(2020, 7, 6)  # YYYY-MM-DD

    # get current date/time
    now = datetime.datetime.now()


    # get stock data within timeframe and store in pandas DataFrame
    df = pdr.get_data_yahoo(stock_ticker, start_date, now)

    # if we have an empty dataframe, make sure to note this using null_return so we can display the error page
    null_return = False
    if df.empty:
        null_return = True
        # return empty lists for all analysis, nothing will be printed on screen apart from the ticker
        return stock_ticker, [], [], [], [], [], null_return

    # TODO: if emas are specific to the perform_min_max_red_blue_white_algorthim, they should only be in that function
    # values in emasUsed are the amount of datapoints observed in the EMA calculation
    emasUsed = [3, 5, 8, 10, 12, 15, 30, 35, 40, 45, 50, 60]

    # make a column in our dataframe for each ema calculation
    for datapoints_count in emasUsed:
        df["Ema_{0}".format(datapoints_count)] = round(df.iloc[:,4].ewm(span=datapoints_count, adjust=False).mean(),2)
    # show more columns in dataframe if needed (console only)
    # pd.set_option('display.max_columns', 500)
    # print(df)

    # IMPORTANT - this loop is where we define our strategy
    # replace the code in here to try out different methods
    analysis, red_blue_white_log, dates, closing_prices, percentage_change_list, rwb_bool = perform_min_max_red_blue_white_algorthim(df, stock_ticker)

    # if only appending to analysis in this function, we can remove assignment
    analysis = analyse_algorithm_output(df, stock_ticker, emasUsed, analysis, percentage_change_list)
   
    return stock_ticker, analysis, red_blue_white_log, dates, closing_prices, rwb_bool, null_return


def perform_min_max_red_blue_white_algorthim(df, ticker):
    """
    Trading Algorithm
    Simple enough formula based on using RED/BLUE/WHITE anlaysis where...
    RED:    corresponds to the minimum exponential moving average (ema) value among the selected short emas (3, 5, 8, 10, 12, 15)
    WHITE:  closing adjusted stock price
    BLUE:   corresponds to the maximum exponential moving average (ema) value among the selected long emas (30, 35, 40, 45, 50, 60)
    """

    # NEXT: iterate through all dates and make calculations and findings
    # CALCULATIONS:
    # cmin and cmax: min value of short (3-15) emas, max of long (30-60)

    in_position = False  # position is True when we have bought a stock
    num = 0
    bp = 0       # buy price, set a time of buying/setting a position
    sp = 0       # sell price
    percentage_change_list = []

    # declare list of analysis statements to be returned
    analysis = []           # this is basically just logs  
    red_blue_white_log = [] # this'll be a tracker for the RBW graph log per adj close
    dates = []              # dates for the graph 
    closing_prices = []     # prices for the graph

    rwb_bool = False    # boolean to keep track of if position is in rwb (buy) or not (sell)

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

        # the date index is a long timestamp and we only wnat the short date
        str_date = timestamp_to_date(date)

        if cmin > cmax:
            # opening position
            rwb_bool = True
            red_blue_white_log.append([str_date, "RED WHITE BLUE", round(close,3)])

            # make the buy if we currently do not hold a position
            if not in_position:
                bp = close
                in_position = True
                analysis.append(log_analysis(date=str_date, price=bp, buy_sell="buy"))
                red_blue_white_log.append([str_date, "BUYING NOW", round(close,3), 'BUY'])

        elif cmin < cmax:
            rwb_bool = False
            # closing position
            red_blue_white_log.append([str_date, "BLUE WHITE RED", round(close,3)])

            # sell if we are in positiont
            if in_position:
                # do the sale
                sp = close
                in_position = False
                analysis.append(log_analysis(date=str_date, price=sp, buy_sell="sell"))
                red_blue_white_log.append([str_date, "SELLING NOW", round(close,3), 'SELL'])

                # calculate % change in price then store in our list of trades/trade evaluations
                pc = (sp/bp-1)*100
                percentage_change_list.append(round(pc,3))

        # check if we still have open position at end of dataframe
        num += 1
        if num == df["Adj Close"].count() and in_position:
            # NOTE: repeated code should be put in func instead but not bothered atm
            # close position

            pos_str = "open" if rwb_bool == True else "close"

            sp = close
            in_position = False
            analysis.append(log_analysis(date=str_date, price=sp, buy_sell="buy", final_price=True, position=pos_str))
            
            red_blue_white_log.append([str_date, "SELLING NOW AT FINAL DATE", round(close,3), 'SELL'])

            # calculate % change in price then store in our list of trades/trade evaluations
            pc = (sp / bp - 1) * 100
            percentage_change_list.append(round(pc,3))

    # print(percentage_change_list)
    analysis.append(["Trade Return Percentages", str(percentage_change_list)])

    return analysis, red_blue_white_log, dates, closing_prices, percentage_change_list, rwb_bool


def analyse_algorithm_output(df, ticker, ema_list, analysis, percentage_change_list):
    """
    perform analysis on an algorithm given certain indicators such as the list of all trades and their percentage returns/losses
    """

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

    # for each percentage_change_list, i.e. outcome of each trade
    # record gains/losses and aggregate final return
    for trade in percentage_change_list:
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
        max_return = max(percentage_change_list)

    if num_losses > 0:
        average_loss = losses/num_losses
        max_loss = min(percentage_change_list)
        gainloss_ratio = (-average_gain/average_loss)
    else:
        average_loss = 0
        max_loss = 0
        gainloss_ratio = average_gain

    # calculate hit ratio, how often trade was a gain
    if num_gains > 0 or num_losses > 0:
        hit_ratio = num_gains/(num_losses+num_gains)

    analysis.append(["EMAs Used", str(ema_list)])
    analysis.append(["Report", make_final_report("EMA RBW", total_return, num_gains, num_losses, average_gain, 
                                        average_loss, max_return, max_loss, hit_ratio, gainloss_ratio)])

    return analysis


def log_analysis(info=None, date=None, price=None, buy_sell=None, final_price=False, position=None, alert=None):
    """
    used to turn analysis tidbits into clean strings that will be printed on screen
    useful for having one place to change/update how these logs look
    info: extra info that we may want to print
    buy_sell: if we are making a log for a buy or sell on our position, buy or sell will be passed in here and the log will be updated accordingly
    final_price: if were at the end of the dataframe, show what position we're in
    alert: if we want to display a certain type of alert (e.g. green box for buy, red for close) we can use this
    """
    analysis_str = []

    if final_price:
        position_str = "an OPEN" if position.lower() == "open" else "a CLOSING"
        return [date, "Current Price at end of Trading Period is {1}. This price is in {2} position. Assume a sale on this price for analysis.".format(date, round(price,3), position_str)]

    if buy_sell.lower() == 'buy':
        return [date, "Buying now @ {1}".format(date, round(price,3))]
    elif buy_sell.lower() == 'sell':
        return [date, "Selling now @ {1}".format(date, round(price,3))]
    

    # if final_price:
    #     position_str = "an OPEN" if position.lower() == "open" else "a CLOSING"
    #     return "{0}: Current Price at end of Trading Period {1}. This price is in {2} position. Assume a sale on this price for analysis.".format(date, round(price,3), position_str)

    # if buy_sell.lower() == 'buy':
    #     return "{0}: Buying now @ {1}".format(date, round(price,3))
    # elif buy_sell.lower() == 'sell':
    #     return "{0}: Selling now @ {1}".format(date, round(price,3))


def make_final_report(algo_name, total_return, num_gains, num_losses, average_gain, average_loss, max_return, max_loss, hit_ratio, gainloss_ratio):

    report_str = "Using the {0} algorithm, the total return was {1} over {2} trades. The average gains and losses were {3} and {4} respectively" \
        " with the maximum gains and losses being {5} and {6}. The hit ratio was {7} and the gain/loss ratio was {8}".format(
            algo_name, total_return, str(num_gains+num_losses), str(round(average_gain,2)), str(round(average_loss,2)), 
            max_return, max_loss, str(round(hit_ratio, 2)), str(round(gainloss_ratio,2))
        )

    # old way
    # add all of these statements to a list to be displayed on screen
    # analysis.append("Results for "+ticker+" going back to "+str(timestamp_to_date(df.index[0]))+", Sample size: "+str(num_gains+num_losses)+" trades")
    # analysis.append("EMAs used: "+str(ema_list))
    # analysis.append("Hit Ratio: "+ str(round(hit_ratio, 2)))
    # analysis.append("Gain/loss ratio: "+str(round(gainloss_ratio,2)))
    # analysis.append("Average Gain: "+str(round(average_gain,2)))
    # analysis.append("Average Loss: "+str(round(average_loss)))
    # analysis.append("Max Return: "+str(max_return))
    # analysis.append("Max Loss: "+str(max_loss))
    # analysis.append("Total return over "+str(num_gains+num_losses)+" trades: "+str(total_return)+"%")

    # this may be useful for printing analysis line by line but use generic report for now
    # analysis.append(["Report", (
    #     "Results for "+ticker+" going back to "+str(timestamp_to_date(df.index[0]))+", Sample size: "+str(num_gains+num_losses)+" trades" + ' <br /> ' \
    #     "EMAs used: "+str(ema_list) + '\n' \
    #     "Hit Ratio: "+ str(round(hit_ratio, 2)) + '\n' \
    #     "Gain/loss ratio: "+str(round(gainloss_ratio,2)) + '\n' \
    #     "Average Gain: "+str(round(average_gain,2)) + '\n' \
    #     "Average Loss: "+str(round(average_loss)) + '\n' \
    #     "Max Return: "+str(max_return) + '\n' \
    #     "Max Loss: "+str(max_loss) + '\n' \
    #     "Total return over "+str(num_gains+num_losses)+" trades: "+str(total_return)+"%"
    #     )
    # ])

    return report_str


def timestamp_to_date(timestamp, return_as_string=False):
    """
    turn pandas timestamp into YYYY-MM-DD format
    """
    if return_as_string:
        return str(timestamp.strftime('%Y-%m-%d'))
    return timestamp.date()
