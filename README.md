# binomialOptions2018

### Overview
This was a project I worked on for a few months in 2018. The idea was to generate reports [like the excel document in the exampleOutput folder](https://github.com/forbesjon2/binomialOptions2018/blob/master/exampleOutput/filter.xlsx) please read the [readme associated with that excel document](https://github.com/forbesjon2/binomialOptions2018/blob/master/exampleOutput/README.md). Some things that appear on that document (and the source code for that matter)are named very improperly. The code needs a solid amount of refactoring as it was made when I was new to the CS area.

The purpose of those reports was to analyze options that appeared to be outliers in regard to their binomial model's pricing in hopes of finding highly asymmetric investments. The next step is to use the data that was collected to analyze the effectiveness of various option strategies. We weren't completely sure of whether this was effective or not as we were provided limited data before our data source made a breaking change (mentioned in the implementation section).

### Implementation
This project was halted because of a change to barchart's option data API, requiring a subscription of sorts. My future plans are to explore other sources of data such as robinhoods unofficial REST API. 

**important note**: the black scholes equation is only effective for European options because they cannot be excercised before expiration. Pricing American stock options is more effective with the binomial options model.

TD Ameritrade API limit: 120 requests/min

### Resources
[Option Pricing: A simplified Approach (1979)](https://citeseerx.ist.psu.edu/viewdoc/citations;jsessionid=2BD640587BAF8D2256C2E22548DEE13D?doi=10.1.1.379.7582)
