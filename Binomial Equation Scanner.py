"""---imports---"""
import re
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

#to save as an exe, type pyinstaller.exe --onefile (--windowed) <filename>.py


"""Miscellaneous math object calling used for yahoo finance & equation"""
sqrt = np.sqrt
e = math.exp

"""http://bradley.bradley.edu/~arr/bsm/pg04.html"""

"""---definition section, adjust these values to change small aspects---"""
Lookback_Length_max = 65               #maximum number of days until expiration
Lookback_Length_min = 10                #minimum number of days until expiration

#minimum total volume, filtered before anything is calculated
Minimum_Volume = 1
Minimum_Open_interest = 10
minimum_option_price = 0.10
minimum_chain_length = 3       #define minimum chain length for calculating the mean of the option valuation calculations
minimum_spread = 10     #define minimum spread (in percent) for the chain to be included in results

#number of branches to be run through the binomial equation
global number_of_branches_low
global number_of_branches_high
number_of_branches_low = 10
number_of_branches_high = 150

Curnt_Interest_Rate = 1.055          #Current interest rate (keep this updated), write in format 1.XX
risk_free_interest_rate = Curnt_Interest_Rate - 1
iterdon = {}
"""https://www.treasury.gov/resource-center/data-chart-center/interest-rates/Pages/TextView.aspx?data=billrates"""

# thinlist thins the results and prints only the results that are optimized for the sort by premium calculation in the binomial equation filter results. Set to false to get generic results 
thinlist = True



"""some date stuff.. ignore this"""
date_object = datetime.datetime.now()
# convert object to the format we want
current_day = int(date_object.strftime('%d'))
current_month = int(date_object.strftime('%m'))
current_year = int(date_object.strftime('%Y'))
comparED = date(current_year, current_month, current_day)
todays_date_man = datetime.date.today()
day_of_week = date_object.strftime('%A')



#splits the full stock list into 4 lists, runs every monday - thursday
#FIXME
day_of_week = "Thursday"
FSL = getStockList.get_stock_list.stock_list_calc(day_of_week)
Full_Stock_List = FSL[0]
#FIXME
Full_Stock_List = ["O"]
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
        ttheq = BinomialEquation.theq(cntr, volatility, days_to_expiration, dividend)
        theqnum, eulers_number_binomial, dte_percent_of_year, UMAD, DMAD = ttheq[0], ttheq[1], ttheq[2], ttheq[3], ttheq[4]

        iterdon = BinomialEquation.itertree(ccounter,UMAD, DMAD, current_price)
        BinomialEquation.intrinsic_value_calculation(theqnum, eulers_number_binomial, iterdon, strike_price, current_price, ccounter, option_type)
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

    def theq(self, volatility, days_to_expiration, dividend):   #input number of branches/volatility/dte, output theqnum/eulers num binomial/dte_percent_of_year/UMAD/DMAD
        dte_percent_of_year = days_to_expiration / 365
        dte_adjusted_to_branch = dte_percent_of_year / self
        dte_adjusted_to_day = dte_percent_of_year / days_to_expiration
        #takes into account dividends as percentage per branch & reduces the gain while increasing the loss respectively on UMAD & DMAD
        if dividend > 0:
            dividend_multiplier = (dividend * dte_percent_of_year) / (self)
        else:
            dividend_multiplier = 0
        UMAD = (e(volatility * sqrt(dte_adjusted_to_branch))) - dividend_multiplier #upawrd movement as fraction, subtract the dividend from upward move [results in smaller upward move and larger downward move]
        DMAD = (e(-volatility * sqrt(dte_adjusted_to_branch))) - dividend_multiplier #downward movement as fraction, subtract (add) the dividend from downward move [results in larger downward move and smaller upward move]

        """we dont need to take into account the calls vs puts because those are reflected in different ways according to the price... the price change affects both upward and downward moves"""
        eulers_number = e(risk_free_interest_rate * dte_adjusted_to_branch)
        eulers_number_binomial = e(-(risk_free_interest_rate * dte_adjusted_to_branch))
        theqnum = ((eulers_number - DMAD) / (UMAD - DMAD))
        return theqnum, eulers_number_binomial, dte_percent_of_year, UMAD, DMAD


    def IVC(self, strike_price, option_type): #where self = iterdon, and the current stock price is imported too. outputs 1 of 2 fundamental values that are to be compared
        """this is the ez calc that is called in intrinsic_value_calculation_call"""
        thisisnotanexit = 0
        strike_price = float(strike_price)
        callcalconedict = {}
        #this is the first part
        for onee in self:
            callcalconelist = []
            #onee returns the keys, self[onee] returns the values
            for indiv in self[onee]:
                if option_type == 'Call':
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

    def intrinsic_value_calculation(self, eulers_number_binomial, iterdon, strike_price, current_price, ccounter, option_type):   #self = theq
        idw = len(iterdon)
        theqnum = self
        first_calculation = BinomialEquation.IVC(iterdon, strike_price, option_type)
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


class Filter:
        def __init__(self):
                pass
#in separate def to increase speed, used only when called
        def bidprice(self):
                bidprice = (re.findall('bidPrice''........', str(self)))
                bidpricee = re.findall('\d?''\d''.''\d''\d?', str(bidprice))
                try:
                        bidpricz = bidpricee[0]
                except:
                        bidpricz = bidpricee
                return bidpricz
        def askprice(self):
                askprice = re.findall('askPrice''........', str(self))
                askpricee = re.findall('\d?''\d''.''\d''\d?', str(askprice))
                try:
                        askrpicz = askpricee[0]
                except:
                        askrpicz = askpricee
                return askrpicz
        def midpoint(self):
                midpoint = re.findall('midpoint''..........', str(self))
                midpointt = re.findall('\d?''\d?''\d?''\d''.''\d''\d?', str(midpoint))
                try:
                        middupont = midpointt[0]
                except:
                        middupont = midpointt
                return middupont
        def strike(self):
                strike = re.findall('strikePrice''..........', str(self))
                strikee = re.findall('\d?''\d?''\d?''\d''.''\d''\d?', str(strike))
                try:
                        strikez = strikee[0]
                except:
                        strikez = strikee
                return strikez
        def volume(self):
                volume = re.findall('volume''.....', str(self))
                volumee = re.findall('\d?''\d?''\d?''\d?''\d', str(volume))
                try:
                        volumeo = volumee[0]
                except:
                        volumeo = volumee
                return volumeo
        #returned as "NA", need to get more familiar with the parmeters before passing thru 2nd line of filtering
        def lastprice(self):
                lastprice = re.findall('lastPrice''..........', str(self))
                lstprce = re.findall('\d?''\d?''\d?''\d''.''\d''\d?', str(lastprice))
                try:
                        lstprcz = lstprce[0]
                except:
                        lstprcz = lstprce
                return lstprcz
        def pcentfl(self):
                pcentfl = re.findall('percentFromLast''.........', str(self))
                return pcentfl
        def openinterest(self):
                openinterest = re.findall('openInterest''..........', str(self))
                openinterestt = re.findall('\d?''\d?''\d?''\d?''\d?''\d', str(openinterest))
                try:
                        oldschool = openinterestt[0]
                except:
                        oldschool = openinterestt
                return oldschool
        def optiontype(self):
                optiontype = re.findall('optionType''.......', str(self))
                optiontypee = re.findall('Call', str(optiontype))
                optiontyper = re.findall('Put', str(optiontype))
                if len(optiontypee) != 0:
                        try:
                                callf = optiontypee[0]
                        except:
                                callf = optiontypee
                        return callf
                else:
                        try:
                                putf = optiontyper[0]
                        except:
                                putf = optiontyper
                        return putf
        def daystoexpiration(self):
                daystoexpiration = re.findall('daysToExpiration''.......', str(self))
                daystoexpirationn = re.findall('\d?''\d?''\d', str(daystoexpiration))
                try:
                        daystoexpiratioz = daystoexpirationn[0]
                except:
                        daystoexpiratioz = daystoexpirationn
                return daystoexpiratioz


#list of def's not inside classes
def url_date(self):
    date_values = {}
    urldatfilterlist = ""
    urll = 'https://core-api.barchart.com/v1/options/chain?'
    date_values['symbol'] = self
    date_values['fields'] = 'expirationDate'
    date_values['groupBy'] = 'optionType'
    date_values['expirationDate'] = 'all'
    dataa = urllib.parse.urlencode(date_values)
    data_stringg = str(dataa)
    ulrr = [urll, data_stringg]
    nothngg = ""
    nothngg = nothngg.join(ulrr)
    nothngg_string = str(nothngg)
    urldatfilterlist = nothngg_string
    return urldatfilterlist


def ccontent(self):
    wwho = []
    headers = {}
    
    headers['User-Agent'] = 'Mozilla/5.0 (X11 Linux i686) AppleWebKit/537.17 (KHTML, like Gecko) Chrome/24.0.1312.27 Safari/537.17'
    respz = urllib.request.Request(self, headers = headers)
    resp = urllib.request.urlopen(respz)
    content = resp.read()
    #separate by strike price
    paragraphs = re.findall(r'{(.*?)}', str(content))
    
    for paragraphh in paragraphs:
        separte = re.findall(r'raw(.*?)expirationDate', str(paragraphh))
    #attaches each individual iteration to the wwho list for future reference
        wwho.append(separte)
    return wwho

def thisistheurlass(self): #filter through the url, call url def
    x = url_date(self)
    
    pesr = urllib.request.urlopen(x)
    dat_content = pesr.read()
    date_values = re.findall(r'\d''\d''\d''\d''.''\d''\d''.''\d''\d', str(dat_content))
    #get the last x dates in list, defined in first few lines
    values = {}
    link_list = []
    url = 'https://core-api.barchart.com/v1/options/chain?'
    #then get the actual URL that should be requested, including dynamic dates

    for indivv in date_values:
        year = int(indivv[0:4])
        month = int(indivv[5:7])
        day = int(indivv[8:10])
        expiration_datezz = date(year, month, day)
        ttime_boi = expiration_datezz - comparED
        lookback_compare = ttime_boi.days
        if lookback_compare <= Lookback_Length_max and lookback_compare >= Lookback_Length_min:
            values['symbol'] = self
            values['fields'] = 'strikePrice,lastPrice,percentFromLast,bidPrice,midpoint,askPrice,priceChange,percentChange,volatility,volume,openInterest,optionType,daysToExpiration,expirationDate,symbolCode,symbolType'
            values['groupBy'] = 'optionType'
            values['expirationDate'] = indivv
            values['raw'] = '1'
            values['meta'] = 'field.shortName,field.type,field.description'
            data = urllib.parse.urlencode(values)
            data_string = str(data)
            ulr = [url, data_string]
            nothng = ""
            nothng = nothng.join(ulr)
            nothng_string = str(nothng)
            link_list.append(nothng_string)
        else:
            pass
    return link_list

def adj_close_values_actually_volatility(self):   #enter individual stock names in self
    llist = []
    orlist2 = []
    innb = 2
    percent_return_list = []
    getdaturl = "https://finance.yahoo.com/quote/" + self + "/history"
    
    open_the_adjvalue = urllib.request.urlopen(getdaturl)
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

def oorganize(self):
        pwkr = thisistheurlass(self)
        raw_llist = []
        #gives a list of all the (to be used) url's all with dynamic date values
        for inlink in pwkr:
                uui = ccontent(inlink)
                uui            #runs uui
        #opens and parses the content from the URL list called from the previous statment. Gets RAW values
                for mink in uui:
                        indivVol = Filter.volume(mink)
                        indivOpenInterest = Filter.openinterest(mink)
                        #indivOptionPrice = Filter.lastprice(mink)
                        indivOptionPrice = Filter.midpoint(mink)
                        try:
                                indivOP = float(indivOptionPrice)
                        except:
                                indivOP = 0
                        try:
                                indivOI = int(indivOpenInterest)
                        except:
                                indivOI = 0
                        try:
                                IntIndiv = int(indivVol)
                        except:
                                IntIndiv = 0
                        #filtering through not NoneType volume
                        #IntIndiv = not NoneType volume, mink = RAW values
                        if IntIndiv >= Minimum_Volume and indivOI >= Minimum_Open_interest and indivOP >= minimum_option_price:
                                raw_llist.append(mink)
        return raw_llist

def columnsz(self):     
        strikpricc = Filter.strike(self)
        expiratin = Filter.daystoexpiration(self)
        bdpricelow = Filter.bidprice(self)
        akprice = Filter.askprice(self)
        optiontypr = Filter.optiontype(self)
        opnintrrst = Filter.openinterest(self)
        mdpnt = Filter.midpoint(self)
        try:
                akkprice = float(str(akprice))
                bddpricelow = float(str(bdpricelow))

                spreadd = (1 - bddpricelow/akkprice) * 100
                spreadzd = round(spreadd, 4)
                actual_spread = str(spreadzd)
        except:
                actual_spread = 'na'
        option_type = str(optiontypr)
        strike_price = str(strikpricc)
        open_interest = str(opnintrrst)
        days_to_expiration = str(expiratin)
        midpoint_option_price = str(mdpnt)
        return option_type, strike_price, open_interest, days_to_expiration, midpoint_option_price, actual_spread

def diividend(self): #input = stock ticker... output = decimal form of percentage of annual dividend
    llist = []
    innb = 2
    percent_return_list = []
    
    getdaturl = "https://finance.yahoo.com/quote/" + self + "/key-statistics"
    open_the_adjvalue = urllib.request.urlopen(getdaturl)
    adjvalue_content = open_the_adjvalue.read()
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
    if call_length >= minimum_chain_length:
        for item in comparable_call:
            comparable_cv.append(item['option valuation'])
        comparable_call_valuation = np.mean(comparable_cv)
    else:
        comparable_call_valuation = 'na'
    if put_length >= minimum_chain_length:
        for iitem in comparable_put:
            comparable_pv.append(item['option valuation'])
        comparable_put_valuation = np.mean(comparable_pv)
    else:
        comparable_put_valuation = 'na'
    return comparable_call_valuation, comparable_put_valuation

def ExAfterEarnings(self):   #enter individual stock names in self
    earnlist = []
    from datetime import datetime
    getdaturl = "https://finance.yahoo.com/quote/" + self
    
    open_the_adjvalue = urllib.request.urlopen(getdaturl)
    adjvalue_contentt = open_the_adjvalue.read()
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
        ccontentm = oorganize(stock)
        get_volatility_list = adj_close_values_actually_volatility(stock)
        annualized_volatility = get_volatility_list[0]
        current_price = round(float(get_volatility_list[1]), 5)
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
        low52kid = get_volatility_list[2]
        comparable_list = []
        comparable_dict = {}

        for oonee in ccontentm:
                results_dict = {}
                temp_list = []
                herer = columnsz(oonee)
                option_typee, strike_pricee, open_interestt, days_to_expirationn, last_option_pricee, actual_spreadd = herer[0], herer[1], herer[2], int(herer[3]), herer[4], herer[5]
                end_date = todays_date_man + timedelta(days = days_to_expirationn)
                actual_spread = float(actual_spreadd)
                if actual_spread >= minimum_spread:
                        pass
                else:
                        results_dict['stock'] = stock
                        results_dict['option type'] = option_typee
                        results_dict['strike price'] = strike_pricee
                        results_dict['expiration date'] = str(end_date)
                        results_dict['days to expiration'] = days_to_expirationn
                        results_dict['current price'] = current_price
                        results_dict['dividend'] = dividend
                        results_dict['annualized volatility'] = annualized_volatility
                        results_dict['open interest'] = open_interestt
                        results_dict['actual spread'] = actual_spreadd
                        results_dict['last option price'] = last_option_pricee
                        binomial_equation_low = BinomialEquation.mngr(current_price_as_list, number_of_branches_low, annualized_volatility, days_to_expirationn, current_price, strike_pricee, option_typee, dividend)
                        results_dict['10 branch binomial equation'] = round(binomial_equation_low[0], 6)
                        temp_list.append(binomial_equation_low)
                        binomial_equation_high = BinomialEquation.mngr(current_price_as_list, number_of_branches_high, annualized_volatility, days_to_expirationn, current_price, strike_pricee, option_typee, dividend)
                        results_dict['150 branch binomial equation'] = round(binomial_equation_high[0], 6)
                        temp_list.append(binomial_equation_high)
                        max_binomial_value = max(temp_list)
                        max_binomial_value = float(max_binomial_value[0])
                        last_option_pricee = float(last_option_pricee)
                        option_valuation = max_binomial_value / last_option_pricee
                        results_dict['option valuation'] = round(option_valuation, 6)
                        results_dict['Days Til ER'] = DaysTilEarnings
                        premium_plus = round((float(last_option_pricee) / float(strike_pricee)), 4)
                        if float(strike_pricee) >= low52kid:
                                results_dict['StrikeBLow'] = 'N'
                        else:
                                results_dict['StrikeBLow'] = 'Y'
                        try:
                                if int(DaysTilEarnings) > days_to_expirationn:
                                        results_dict['ExAfterEarnings'] = 'N' #fav
                                elif int(DaysTilEarnings) <= days_to_expirationn:
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

        
for stock in Full_Stock_List:
        
        csc += 1
        csc_percent = (csc / length_stock_list) * 100
        print(csc_percent)

        testthis = csc%100
        if (testthis == 0):
                time.sleep(250)
        else:
                pass

        try:
                comparable_list = mainn(stock)

        except:
                error = sys.exc_info()
                print("error: " + str(error))
                stock_error_list.append(stock)

stock_error_list_two = []

for stockt in stock_error_list:
        time.sleep(3)
        try:
                mainn(stockt)
        except:
                stock_error_list_two.append(stockt)

for stockk in stock_error_list_two:
        time.sleep(3)
        try:
                mainn(stockk)
        except:
                pass

import main

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
        main.mail.sendMail("forbesjon2@gmail.com", "forbesjon2@gmail.com", "scan results", content)
        savefile2.close()
else:
        pass