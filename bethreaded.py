"""---imports---"""
from distutils.log import error
from json.tool import main
from queue import Full
from unittest import result
from unittest.mock import call
import numpy as np
import statistics as st
import math
import datetime
from datetime import date
from datetime import timedelta
import sys
import time
import csv
import ssl
import multiprocessing
from td.client import TDClient

#Prevent TD Ameritrade API from throwing SSLError
ssl._create_default_https_context = ssl._create_unverified_context

#Get TD Ameritrade API key. creds.txt is a text file with API key as the only text
API_KEY = open('creds.txt', 'r').read()
# Create a new session, credentials path is required.
TDSession = TDClient(
    client_id=API_KEY,
    redirect_uri='https://127.0.0.1',
    credentials_path='/Users/forbesjon2/Desktop/binomialOptions2018/td_state.json'
)
TDSession.login()

"""Miscellaneous math object calling used for yahoo finance & equation"""
sqrt = np.sqrt
e = math.exp

"""http://bradley.bradley.edu/~arr/bsm/pg04.html"""

"""---definition section, adjust these values to change small aspects---"""
lookback_len_max = 500               #maximum number of days until expiration
lookback_len_min = 30                #minimum number of days until expiration

#minimum total volume, filtered before anything is calculated
min_volume = 1
min_open_interest = 600
# NOT ENFORCED min_option_price = 0.10
min_chain_length = 3       #define minimum chain length for calculating the mean of the option valuation calculations
# NOT ENFORCED min_spread = 25     #define minimum spread (in percent) for the chain to be included in results
strike_count = 12   #number of strikes to return above and below the at-the-money price (x above, x below)

#number of branches to be run through the binomial equation
global num_branches_low
global num_branches_high
num_branches_low = 10
num_branches_high = 150

INTEREST_RATE = 1.015          #Current interest rate (keep this updated), write in format 1.XX UPDATE-Not sure about this one
risk_free_interest_rate = INTEREST_RATE - 1
iterdon = {}
"""https://www.treasury.gov/resource-center/data-chart-center/interest-rates/Pages/TextView.aspx?data=billrates"""

debug = True
BLOCK_LIST = []

"""some date stuff.. ignore this"""
date_object = datetime.datetime.now()
# convert object to the format we want
current_day = int(date_object.strftime('%d'))
current_month = int(date_object.strftime('%m'))
current_year = int(date_object.strftime('%Y'))
comparED = date(current_year, current_month, current_day)
todays_date_man = datetime.date.today()
day_of_week = date_object.strftime('%A')

# Lookback length as a date string (yyyy-MM-DD format)
lb_len_max_date = (datetime.datetime.now() + datetime.timedelta(days=lookback_len_max)).strftime('%Y-%m-%d')
lb_len_min_date = (datetime.datetime.now() + datetime.timedelta(days=lookback_len_min)).strftime('%Y-%m-%d')


#splits the full stock list into 4 lists, runs every monday - thursday
#FIXME
day_of_week = "Thursday"

# Zacks custom screen columns: Company Name,Ticker,Market Cap (mil),Optionable,Dividend ,Next EPS Report Date  (yyyymmdd)
Full_Stock_List = []
with open('zacks_custom_screen.csv', 'r') as file:
    for line in csv.reader(file):
        Full_Stock_List.append(line)
Full_Stock_List = Full_Stock_List[1::]

# FSL = getStockList.get_stock_list.stock_list_calc(day_of_week)

#FIXME
# Full_Stock_List = ["RAVN"]
writeMode = 'a'
if writeMode == "na":
        sys.exit()
else:
        pass
#test1 dow = sunday, stock = aa


"""---class and def section---"""
class BinomialEquation():
    def __init__(self):
        pass

    def mngr(self, cntr, volatility, days_to_expiration, current_price, strike_price, option_type, dividend):
        ccounter = cntr
        global markcounbter
        markcounbter = cntr
        global calc_dict
        calc_dict = {}
        #no affect whether calls vs puts
        ttheq = BinomialEquation.theq(self, cntr, volatility, days_to_expiration, dividend)
        print_debug("ttheq: " + str(ttheq))
        theqnum, eulers_number_binomial, dte_percent_of_year, UMAD, DMAD = ttheq[0], ttheq[1], ttheq[2], ttheq[3], ttheq[4]
        iterdon = BinomialEquation.itertree(self, ccounter, UMAD, DMAD, current_price)
        BinomialEquation.intrinsic_value_calculation(self, theqnum, eulers_number_binomial, iterdon, strike_price, current_price, ccounter, option_type)
        beresult = calc_dict[1]
        return beresult

    def itertree(self, ccounter, UMAD, DMAD, current_price):
        thedict = {}
        cntr = ccounter
        for numberr in range (0, ccounter +1):
            thellist = []
            cntr -= 1
            counter2 = cntr + 1
            for num in range(0, counter2 + 1):
                up = counter2 - num
                down = num
                upcalc =  ((UMAD**up) *(DMAD**down)) *(current_price)
                thellist.append(upcalc)
                num += 1
            thedict[len(thellist)] = thellist
        return thedict

    def theq(self, cntr, volatility, days_to_expiration, dividend):   #input number of branches/volatility/dte, output theqnum/eulers num binomial/dte_percent_of_year/UMAD/DMAD
        dte_percent_of_year = days_to_expiration / 365
        dte_adjusted_to_branch = dte_percent_of_year / cntr
        dte_adjusted_to_day = dte_percent_of_year / days_to_expiration
        #takes into account dividends as percentage per branch & reduces the gain while increasing the loss respectively on UMAD & DMAD
        if dividend > 0:
            dividend_multiplier = (dividend * dte_percent_of_year) / cntr
        else:
            dividend_multiplier = 0
        UMAD = (e(volatility * sqrt(dte_adjusted_to_branch))) - dividend_multiplier #upawrd movement as fraction, subtract the dividend from upward move [results in smaller upward move and larger downward move]
        DMAD = (e(-volatility * sqrt(dte_adjusted_to_branch))) - dividend_multiplier #downward movement as fraction, subtract (add) the dividend from downward move [results in larger downward move and smaller upward move]

        """we dont need to take into account the calls vs puts because those are reflected in different ways according to the price... the price change affects both upward and downward moves"""
        eulers_number = e(risk_free_interest_rate * dte_adjusted_to_branch)
        eulers_number_binomial = e(-(risk_free_interest_rate * dte_adjusted_to_branch))
        theqnum = ((eulers_number - DMAD) / (UMAD - DMAD))
        return theqnum, eulers_number_binomial, dte_percent_of_year, UMAD, DMAD


    def IVC(self, iterdon, strike_price, option_type): #where the current stock price is imported. outputs 1 of 2 fundamental values that are to be compared
        """this is the ez calc that is called in intrinsic_value_calculation_call"""
        thisisnotanexit = 0
        strike_price = float(strike_price)
        callcalconedict = {}
        #this is the first part
        for onee in iterdon:
            callcalconelist = []
            #onee returns the keys, iterdon[onee] returns the values
            for indiv in iterdon[onee]:
                if option_type == 'CALL':
                    onme = indiv - strike_price
                else:
                    onme = strike_price - indiv
                if onme <= 0:
                    onme = 0
                    callcalconelist.append(onme)
                else:
                    callcalconelist.append(onme)
            callcalconedict[len(callcalconelist)] = callcalconelist
            thisisnotanexit += 1
        return callcalconedict

    def intrinsic_value_calculation(self, theqnum, eulers_number_binomial, iterdon, strike_price, current_price, ccounter, option_type):
        idw = len(iterdon)
        first_calculation = BinomialEquation.IVC(self, iterdon, strike_price, option_type)
        first_calc_length = (len(first_calculation)) - 1   #-1 because there are n -1 calculated branches total
        while first_calc_length != 0: #prepares a n + 1 branch for binomial
            calctwolist = first_calculation[first_calc_length + 1] #-1 every iteration, begins at end
            #(callcalctwolist) #goes from last list in dict to first
            iterate_one = len(calctwolist) - 1
            iterate_two = 0
            binomial_list = []
            """attaches farthest branch to final tree"""
            if (first_calc_length + 1) == idw:
                calc_dict[idw] = first_calculation[first_calc_length + 1]
            else:
                pass
            while iterate_two != iterate_one:
                calc_dict_setup = calc_dict[first_calc_length + 1]
                firstnum, secondnum = calc_dict_setup[iterate_two], calc_dict_setup[iterate_two + 1]
                biinomial_value_calculation = ((firstnum) * (theqnum) + (secondnum) *(1 - theqnum)) * eulers_number_binomial
                ez_calc = first_calculation[iterate_one]
                ez_calc_result = ez_calc[iterate_two]
                iterate_two += 1

                #attach the larger of the two calculations onto the binomial list
                if biinomial_value_calculation > ez_calc_result:
                    binomial_list.append(biinomial_value_calculation)
                elif ez_calc_result > biinomial_value_calculation:
                    binomial_list.append(ez_calc_result)
                else:
                    binomial_list.append(ez_calc_result)

                if iterate_two == iterate_one:
                    calc_dict[iterate_two] = binomial_list
                else:
                    pass
            first_calc_length -= 1
        return calc_dict

#Returns list of filtered options, underlying stock info
def get_option_data(symbol):
    opt_chain = {
        'symbol': symbol,
        'contractType': 'ALL',
        'fromDate': lb_len_min_date,
        'toDate': lb_len_max_date,
        'strikeCount': strike_count,
        'includeQuotes': True,
        'range': 'ALL',
        'strategy': 'SINGLE'
    }
    option_chain = TDSession.get_options_chain(option_chain=opt_chain)
    if option_chain["status"] != "SUCCESS":
        print_debug("get_option_data failed for " + symbol)
        return None
    option_data = []
    for option_type in ["callExpDateMap", "putExpDateMap"]:
        for option_date in option_chain[option_type]:
            for option_strike in option_chain[option_type][option_date]:
                if filter_option(option_chain[option_type][option_date][option_strike][0]):
                    option_chain[option_type][option_date][option_strike][0]["option_date"] = option_date
                    option_data.append(option_chain[option_type][option_date][option_strike][0])
    return option_data, option_chain["underlying"]

def filter_option(option_dict):
    if option_dict["ask"] == 0 or option_dict["bid"] == 0 or option_dict["mark"] == 0:
        return False
    res = option_dict["totalVolume"] < min_volume
    res |= option_dict["openInterest"] < min_open_interest
    # res |= option_dict["last"] < min_option_price
    # res |= abs((round(float(option_dict["bid"] / option_dict["ask"]), 4)) * 100) < min_spread
    return not res

def get_volatility(self):   #enter individual stock names in self
    close_list = []
    low_list = []
    innb = 2
    percent_return_list = []
    price_hist = TDSession.get_price_history(symbol=self, period_type='year', frequency_type='daily')
    
    if len(price_hist['candles']) == 0:
        print_debug("get_price_history failed for " + self)
        return None

    for item in price_hist['candles']:
        low_list.append(item['low'])
        close_list.append(item['close'])
     
    #this prints the current price of the stock, as of the most recent adjusted close price
    while innb < 300:
        try:
            denominator = float(close_list[innb-2])
            numerator = float(close_list[innb-1])
            percent_returnn = ((numerator/denominator) - 1)
            returnss = round(percent_returnn, 8) #rounds to 8 decimal places
            percent_return_list.append(returnss)
        except:
            pass
        innb +=1
    
    low52 = round(float(min(low_list)), 3)
    volatilimmmty = st.stdev(percent_return_list)
    volatility = sqrt(252)*volatilimmmty
    illist = close_list[0]
    return volatility, illist, low52


def BEaverage(self):
    comparable_call = []
    comparable_put = []
    comparable_cv = []
    comparable_pv = []
    for item in self:
        typert = item['option type']
        if typert == 'Call':
            comparable_call.append(item)
        else:
            comparable_put.append(item)    
    call_length = len(comparable_call)
    put_length = len(comparable_put)
    if call_length >= min_chain_length:
        for item in comparable_call:
            comparable_cv.append(item['option valuation'])
        comparable_call_valuation = np.mean(comparable_cv)
    else:
        comparable_call_valuation = 'na'
    if put_length >= min_chain_length:
        for iitem in comparable_put:
            comparable_pv.append(item['option valuation'])
        comparable_put_valuation = np.mean(comparable_pv)
    else:
        comparable_put_valuation = 'na'
    return comparable_call_valuation, comparable_put_valuation

def mainn(stock_data):
    stock = stock_data[1]
    dividend = float(stock_data[4]) / 100.0
    print_debug("diividend: " + str(dividend) + " for stock:" + stock)
    # option_data = oorganize(stock)
    option_data, underlying = get_option_data(stock_data[1])
    # print_debug("option_data: " + str(option_data))
    if option_data == None:
        return []

    get_volatility_list = get_volatility(stock)
    print_debug("volatility list: " + str(get_volatility_list))
    annualized_volatility = get_volatility_list[0]
    current_price = round(float(get_volatility_list[1]), 5)
    print_debug("current_price: " + str(current_price))
    try:
        if stock_data[5] == "":
            DaysTilEarnings = 'na'
        earnings_date = datetime.datetime.strptime(stock_data[5],"%Y%m%d")
        current_date = datetime.datetime.today()
        DaysTilEarnings = str((earnings_date - current_date).days) #ExAfterEarnings(stock)
        if int(DaysTilEarnings) < 0:
            DaysTilEarnings = 'na'
    except:
        DaysTilEarnings = 'na'
    current_price_as_list = []
    current_price_as_list.append(current_price)
    fifty2_week_low = underlying["fiftyTwoWeekLow"] #old get_volatility_list[2]
    print_debug("fifty2_week_low: " + str(fifty2_week_low))
    comparable_list = []
    comparable_dict = {}

    for option in option_data:
        results_dict = {}
        temp_list = []    
        # spread = float(round(((1 - option["ask"]/option["bid"]) * 100.0), 4))
        end_date = todays_date_man + timedelta(days = option["daysToExpiration"])
        if True:
            results_dict = {
                "stock": stock,
                "option type": option["putCall"],
                "strike price": option["strikePrice"],
                "expiration date": str(end_date),
                "days to expiration": option["daysToExpiration"],
                "current price": current_price,
                "dividend": dividend,
                "annualized volatility": annualized_volatility,
                "open interest": option["openInterest"],
                "actual spread": 0,
                "last option price": str(option["mark"])
            }
            print_debug("results_dict: " + str(results_dict))
            binomial_equation_low = BinomialEquation.mngr(current_price_as_list, num_branches_low, annualized_volatility, option["daysToExpiration"], current_price, option["strikePrice"], option["putCall"], dividend)
            results_dict['10 branch binomial equation'] = round(binomial_equation_low[0], 6)
            temp_list.append(binomial_equation_low)
            binomial_equation_high = BinomialEquation.mngr(current_price_as_list, num_branches_high, annualized_volatility, option["daysToExpiration"], current_price, option["strikePrice"], option["putCall"], dividend)
            results_dict['150 branch binomial equation'] = round(binomial_equation_high[0], 6)
            temp_list.append(binomial_equation_high)
            max_binomial_value = max(temp_list)
            max_binomial_value = float(max_binomial_value[0])
            option_valuation = max_binomial_value / option["mark"]
            results_dict['option valuation'] = round(option_valuation, 6)
            results_dict['Days Til ER'] = DaysTilEarnings
            premium_plus = round((float(option["mark"]) / float(option["strikePrice"])), 4)
            if float(option["strikePrice"]) >= fifty2_week_low:
                    results_dict['StrikeBLow'] = 'N'
            else:
                    results_dict['StrikeBLow'] = 'Y'
            try:
                    if int(DaysTilEarnings) > option["daysToExpiration"]:
                            results_dict['ExAfterEarnings'] = 'N' #fav
                    elif int(DaysTilEarnings) <= option["daysToExpiration"]:
                            results_dict['ExAfterEarnings'] = 'Y'
                    else:
                            pass
            except:
                    results_dict['ExAfterEarnings'] = 'na'
            results_dict['premium plus'] = premium_plus
            
            comparable_list.append(results_dict)
            saveFile.write(str(results_dict) + '\n')
            saveFile.flush()

            # if (option_valuation < 0.1 and premium_plus > 0.02):
            #         comparable_list.append(results_dict)
            #         saveFile.write(str(results_dict) + '\n')
            #         saveFile.flush()
            # else:
            #         pass
    return comparable_list


def print_debug(content):
    if debug:
        file = open("debug.txt", 'a')
        file.write(str(content))
        file.write("\n")
        file.close()


"""comparable list, not needed for now""" 
#        be_average = BEaverage(comparable_list)
#       comparable_call_valuation = be_average[0]
#       comparable_put_valuation = be_average[1]
#       comparable_dict['stock'] = stock
#       comparable_dict['comparable call valuation'] = comparable_call_valuation
#       comparable_dict['comparable put valuation'] = comparable_put_valuation

#       saveFile.write(str(comparable_dict))
#       saveFile.write('\n')
#       saveFile.flush()

def iterate_list(stock_list, id, error_list):
    csc = 0
    for item in stock_list:
        if item[1] in BLOCK_LIST or str(item[1]).find(".") != -1:
            print("skipping " + item[1])
            continue
        csc += 1
        csc_percent = (csc / len(stock_list)) * 100
        print(str(round(csc_percent, 2)) + "% done for thread" + id)
        try:
            mainn(item)
        except:
            error = sys.exc_info()
            print("error: " + str(error))
            error_list.append(item)


def split_list(alist, wanted_parts=1):
    length = len(alist)
    return [alist[i*length // wanted_parts: (i+1)*length // wanted_parts] 
             for i in range(wanted_parts)]


saveFile = open("Fjin.txt", writeMode)
if writeMode == 'a':
        saveFile.write('\n')

if __name__ == "__main__":
    manager = multiprocessing.Manager()
    error_list = manager.list()
    """---open and write to file. If its monday, the file contents reset---"""

    """---main program---"""
    #saveFile.write('Format: [Stock, option type, strike price, days to expiration, current price, dividend, annualized volatility, open interest, actual spread (in %), last option price, 10 branch binomial equation, 150 branch binomial equation, option valuation (max of 10 or 150 branch divided by last traded option price)]\n')
    results_list = []
    stock_error_list = []
    Full_Stock_List = split_list(Full_Stock_List, 1)
    process1 = multiprocessing.Process(target=iterate_list, args=[Full_Stock_List[0], "A", error_list])
    # process2 = multiprocessing.Process(target=iterate_list, args=[Full_Stock_List[1], "B", error_list])
    process1.start()
    # process2.start()
    process1.join()
    # process2.join()
    print("done: here is the error_list:")
    print(error_list)
    # import main

    saveFile.flush()
    saveFile.close()