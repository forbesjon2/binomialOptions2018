"""---imports---"""
import re
from unittest import result
from unittest.mock import call
import urllib.request
import urllib.parse
import numpy as np
import statistics as st
import time
import math
import operator
import datetime
from datetime import date
from datetime import timedelta
import sys
import getStockList
import ssl
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
lookback_len_max = 65               #maximum number of days until expiration
lookback_len_min = 10                #minimum number of days until expiration

#minimum total volume, filtered before anything is calculated
min_volume = 1
min_open_interest = 10
min_option_price = 0.10
min_chain_length = 3       #define minimum chain length for calculating the mean of the option valuation calculations
min_spread = 10     #define minimum spread (in percent) for the chain to be included in results

#number of branches to be run through the binomial equation
global num_branches_low
global num_branches_high
num_branches_low = 10
num_branches_high = 150

INTEREST_RATE = 1.055          #Current interest rate (keep this updated), write in format 1.XX
risk_free_interest_rate = INTEREST_RATE - 1
iterdon = {}
"""https://www.treasury.gov/resource-center/data-chart-center/interest-rates/Pages/TextView.aspx?data=billrates"""

# thinlist thins the results and prints only the results that are optimized for the sort by premium calculation in the binomial equation filter results. Set to false to get generic results 
thinlist = True
debug = True


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
FSL = getStockList.get_stock_list.stock_list_calc(day_of_week)
Full_Stock_List = FSL[0]
#FIXME
# Full_Stock_List = ["RAVN"]
writeMode = FSL[1]

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
def get_option_data(self):
    opt_chain = {
        'symbol': self,
        'contractType': 'ALL',
        'fromDate': lb_len_min_date,
        'toDate': lb_len_max_date,
        'includeQuotes': True,
        'range': 'ALL',
        'strategy': 'SINGLE'
    }
    option_chain = TDSession.get_options_chain(option_chain=opt_chain)
    if option_chain["status"] != "SUCCESS":
        print_debug("get_option_data failed for " + self)
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
    if option_dict["ask"] == 0 or option_dict["bid"] == 0:
        return False
    res = option_dict["totalVolume"] < min_volume
    res |= option_dict["openInterest"] < min_open_interest
    res |= option_dict["last"] < min_option_price
    res |= (round(float(option_dict["bid"] / option_dict["ask"]), 4)) * 100 < min_spread
    return not res

def get_volatility(self):   #enter individual stock names in self
    llist = []
    orlist2 = []
    innb = 2
    percent_return_list = []
    url = "https://finance.yahoo.com/quote/" + self + "/history"
    headers = {}
    headers['User-Agent'] = 'Mozilla/5.0 (X11 Linux i686) AppleWebKit/537.17 (KHTML, like Gecko) Chrome/24.0.1312.27 Safari/537.17'
    pre_req = urllib.request.Request(url, headers = headers)
    open_the_adjvalue = urllib.request.urlopen(pre_req)
    adjvalue_content = open_the_adjvalue.read()
    what = re.findall(r'adjclose":(.*?)}', str(adjvalue_content))
    otherwhat = re.findall(r'"low":(.*?),"', str(adjvalue_content))
    
    for neo in otherwhat:
        try:
            orlist2.append(neo)
        except:
            pass
    for oen in what:
        try:
            llist.append(oen)
        except:
            pass
    #this prints the current price of the stock, as of the most recent adjusted close price
    while innb < 300:
        try:
            denominator = float(llist[innb-2])
            numerator = float(llist[innb-1])
            percent_returnn = ((numerator/denominator) - 1)
            returnss = round(percent_returnn, 8) #rounds to 8 decimal places
            percent_return_list.append(returnss)
        except:
            pass
        innb +=1
    low52 = round(float(min(orlist2)), 3)
    volatilimmmty = st.stdev(percent_return_list)
    volatility = sqrt(252)*volatilimmmty
    illist = llist[0]
    return volatility, illist, low52


def diividend(self): #input = stock ticker... output = decimal form of percentage of annual dividend
    headers = {}
    headers['User-Agent'] = 'Mozilla/5.0 (X11 Linux i686) AppleWebKit/537.17 (KHTML, like Gecko) Chrome/24.0.1312.27 Safari/537.17'
    request = urllib.request.Request("https://finance.yahoo.com/quote/" + self + "/key-statistics", headers = headers)
    adjvalue_content = urllib.request.urlopen(request).read()
    what = re.findall(r'dividendYield":{"raw":(.*?),', str(adjvalue_content))
    wuwut = re.findall(r'yield":{"raw":(.*?),"', str(adjvalue_content))
    print(self)
    if len(what) > 0:
        whatfloat = float(what[0])
        if whatfloat > 0:
            dividend = whatfloat
        else:
            dividend = 0
    elif len(wuwut) > 0:
        wwhatfloat = float(wuwut[0])
        if wwhatfloat > 0:
            dividend = wwhatfloat
        else:
            dividend = 0
    else:
        dividend = 0
    return dividend

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

def ExAfterEarnings(self):   #enter individual stock names in self
    earnlist = []
    from datetime import datetime
    headers = {}
    headers['User-Agent'] = 'Mozilla/5.0 (X11 Linux i686) AppleWebKit/537.17 (KHTML, like Gecko) Chrome/24.0.1312.27 Safari/537.17'
    request = urllib.request.Request("https://finance.yahoo.com/quote/" + self, headers = headers)
    adjvalue_contentt = urllib.request.urlopen(request).read()
    firstfiltr = re.findall(r'"EARNINGS_DATE-value"(.*?)</span></td></tr>', str(adjvalue_contentt))
    sndfiltr = re.findall('\w\w\w\s\d\d?.\s\d\d\d\d', str(firstfiltr))
    for itemm in sndfiltr:
        curntdate = datetime.strptime(itemm, '%b %d, %Y')
        curntdate = str(curntdate)
        theyear = int(curntdate[0:4])
        themonth = int(curntdate[5:7])
        theday = int(curntdate[8:10])
        from datetime import date
        orthismanidk = date(theyear, themonth, theday)
        ttime_kid = orthismanidk - comparED
        comparetimekid = ttime_kid.days
        if comparetimekid < -200: #sometimes yahoo puts in the past year but the correct month/day, this corrects that mistake
            comparetimekid = comparetimekid + 365
        earnlist.append(comparetimekid)
    farearnings = min(earnlist)
    return farearnings



def mainn(self):
    stock = self
    dividend = diividend(stock)
    print_debug("diividend: " + str(dividend))
    # option_data = oorganize(stock)
    option_data, underlying = get_option_data(self)
    print_debug("option_data: " + str(option_data))
    if option_data == None:
        return []

    get_volatility_list = get_volatility(stock)
    print_debug("volatility list: " + str(get_volatility_list))
    annualized_volatility = get_volatility_list[0]
    current_price = round(float(get_volatility_list[1]), 5)
    print_debug("current_price: " + str(current_price))
    try:
        DaysTilEarnings = ExAfterEarnings(stock)
        if int(DaysTilEarnings) < 0:
            DaysTilEarnings = 'na'
        else:
            pass
    except:
        DaysTilEarnings = 'na'
    current_price_as_list = []
    current_price_as_list.append(current_price)
    fifty2_week_low = underlying["fiftyTwoWeekLow"] #old get_volatility_list[2]
    print_debug("fifty2_week_low: " + str(fifty2_week_low))
    comparable_list = []
    comparable_dict = {}

    for option in option_data:
        print(option["description"])
        results_dict = {}
        temp_list = []    
        spread = float(round(((1 - option["ask"]/option["bid"]) * 100.0), 4))
        end_date = todays_date_man + timedelta(days = option["daysToExpiration"])
        if spread >= min_spread:
                pass
        else:
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
                "actual spread": spread,
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




"""---open and write to file. If its monday, the file contents reset---"""
saveFile = open("Fjin.txt", writeMode)
if writeMode == 'a':
        saveFile.write('\n')
"""---main program---"""
#saveFile.write('Format: [Stock, option type, strike price, days to expiration, current price, dividend, annualized volatility, open interest, actual spread (in %), last option price, 10 branch binomial equation, 150 branch binomial equation, option valuation (max of 10 or 150 branch divided by last traded option price)]\n')
results_list = []
stock_error_list = []

#calculate percentage done
length_stock_list = len(Full_Stock_List)

csc = 0
print_debug(Full_Stock_List)
        
for stock in Full_Stock_List:
    csc += 1
    csc_percent = (csc / length_stock_list) * 100
    print(str(csc_percent) + " % done")

    testthis = csc%100
    if (testthis == 0):
            time.sleep(250)
    else:
            pass
    try:
        comparable_list = mainn(stock)
        time.sleep(2)
        print_debug("Comparable list " + str(comparable_list))
    except:
        error = sys.exc_info()
        print("error: " + str(error))
        stock_error_list.append(stock)

for stockt in stock_error_list:
    time.sleep(3)
    try:
        mainn(stockt)
    except:
        pass


# import main

saveFile.flush()
saveFile.close()

"""sendmail idea here is outdated, filter and then send..."""
# def contentConversion(content):
#         content2 = ('copy & paste into excel for better reading format')
#         content2 += ("\nSort by premium\n\n")
#         content2 += ('stock\toption type\texpiration date\tstrike price\tDTE\tcurrent price\tdividend\tannualVTY\topen interest\tactual spread\tlast option price\t10 branch BE\t150 branch BE\toption valu\tDTER\tBelow52wk\tExp aftr ER\tPremium plus\n')
#         for dictt in content:
#                 print(dictt)
#                 print(str(dictt['stock']) +  '\t' + str(dictt['option type']) +  '\t' + str(dictt['expiration date']) +'\t' + str(dictt['strike price']) + '\t' + str(dictt['days to expiration']) + '\t' + str(dictt['current price']) + '\t' + str(dictt['dividend']) + '\t' + str(round(dictt['annualized volatility'], 4))  + '\t' + str(dictt['open interest']) + '\t' + str(dictt['actual spread']) + '\t' + str(dictt['last option price']) + '\t' + str(dictt['10 branch binomial equation']) + '\t' + str(dictt['150 branch binomial equation']) + '\t' + str(dictt['option valuation']) + '\t' + str(dictt['Days Til ER']) + '\t'+ str(dictt['StrikeBLow']) + '\t' + str(dictt['ExAfterEarnings']) + '\t' + str(dictt['Premium plus']))
#         return content2

time.sleep(10)
#send email of the complete results if its thursday, else just do nothing
if day_of_week == "Thursday":
        savefile2 = open('fjin.txt', 'r')
        content = savefile2.read()
        # mailContent = contentConversion(content)
        savefile2.close()
else:
        pass