options that qualify must have...
minimum volume of 30
minimum open interest of 500
minimum price of 0.10
minimum spread of less than 13%
have an expiration date later than 35 and earlier than 80 days




Potential inaccuracies...

The dividend is calculated as a fraction of an annual percentage depending on the days to expiration... not by days to ex dividend & amount paid that date
	the option chains that may be affected by this the most are ones that expire the soonest. any other 
General unanticipated errors, before buying be sure to check to make sure that the numbers in the excel document arent inaccurate

If you search for "e-" in the document it will point you to a few options who ended up unsorted because their 10 & 150 branch binomial equation calculation didnt even register the kind
of movements that the market is predicting (some times the 10 branch binomial equation doesnt even register a number). This is not an error.. it sources from the last years price action,
calculated as the volatility in the binomial equation.





Terms used in asymmetry comparison columns (top of page)

CCall: comparable call valuation...
	if a stock has a chain of 3 or more call options, the mean of the option valuation of all existing call options are taken for that one stock... regardless of expiration date
CPut: comparable put valuation...
	if a stock has a chain of 3 or more put options, the mean of the option valuation of all existing put options are taken for that one stock... regardless of expiration date
both CCall and CPut groups options together to be used as inputs to measure asymmetry, its much more accurate than

asymmetry: the larger number between both CCall and CPut is taken and divided by the smaller number between CCall and CPut
...this turns the asymmetry into a ratio.
	smaller = less asymmetrical
	larger = more asymmetrical
Note: numbers around 1 mean that there is little to no asymmetry & the opposite for larger numbers.



Terms used in individual option chain comparison (left side filters through chains with an option valuation under 0.1 and greater than 2)
	Note: numbers that end in a large number that end with e-XXX are actually very small numbers. Excel doesnt recognize numbers such as 10.0E-5 as 0.0001

option valuation: the larger number between both 10 branch binomial equation and 150 branch binomial equation is divided by the last traded option price
	smaller = more "overvalued"
	larger = more "undervalued"
StrikeBLow: Shows if the strike price is above or below the 52 week low
	Y = strike price is below the 52 week low
	N = strike price is above the 52 week low
ExAfterEarnings: Tells you if the stock expires after earnings are released. Sometimes yahoo gives you two dates, the date that is closer to the current date will be used in that case. For
smaller stocks, the data may not be updated.. in that case an 'na' is returned. Its importatnt to check this just to make sure the numbers are valid
	Y = between now and the expiration date, earnings will be released
	N = no earnings will be released between now and the expiration date
	na = the stock either has a very small market cap (unlikely) or its an ETF



1-20-18 new changes
moved the DTE column to near the end, replaced it with Expiration date (for easier access when looking up the chains)

Premium plus: increases the profit per dollar invested...
	this is done by dividing the last traded option price by the net value of the option.

Brokerages require you to hold a certain amount of cash in your account when selling an option calculated by factoring in the option premium and X% of the underlying stocks price. Using this
calculation, we avoid investing a lot of money into positions that wont give us much return per dollar invested. 


**Note: the option valu(ation) column is no longer being sorted from most undervalued to overvalued...
the column that is now being sorted is the premium plus (to increase profit per dollar invested)
	

