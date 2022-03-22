import json
import csv
import math

fieldNames =['stock', 'option type', 'strike price', 'expiration date', 'days to expiration', 'current price', 'dividend', 'annualized volatility', 'open interest', 'last option price', '10 branch binomial equation', '150 branch binomial equation', 'option valuation', 'Days Til ER', 'StrikeBLow', 'ExAfterEarnings', 'premium plus', 'mean diff', 'actual spread']
file = open("Fjin.txt", 'r')

data = []
for line in file.readlines():
    line = line.replace("'", "\"")
    try:
        line = json.loads(line)
    except:
        continue
    line["mean diff"] = (abs(line["10 branch binomial equation"] - float(line["last option price"]))) + (abs(line["150 branch binomial equation"] - float(line["last option price"])))
    line["mean diff"] /= 2.0
    line["mean diff"] /= float(line["last option price"])
    if line["open interest"] > 1000:
        data.append(line)
# data = sorted(data, key=lambda item: item.get(""))
with open('out.csv', 'w') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames = fieldNames)
    writer.writeheader()
    writer.writerows(data)

print(data[0])

# content = json.loads([0].replace("\n", ""))
# print(file.readlines(1)[0].replace("\n", ""))

# content2 = ('copy & paste into excel for better reading format')
# content2 += ("\nSort by premium\n\n")
# content2 += ('stock\toption type\texpiration date\tstrike price\tDTE\tcurrent price\tdividend\tannualVTY\topen interest\tactual spread\tlast option price\t10 branch BE\t150 branch BE\toption valu\tDTER\tBelow52wk\tExp aftr ER\tPremium plus\n')
# for dictt in content:
#         print(dictt)
        # print(str(dictt['stock']) +  '\t' + str(dictt['option type']) +  '\t' + str(dictt['expiration date']) +'\t' + str(dictt['strike price']) + '\t' + str(dictt['days to expiration']) + '\t' + str(dictt['current price']) + '\t' + str(dictt['dividend']) + '\t' + str(round(dictt['annualized volatility'], 4))  + '\t' + str(dictt['open interest']) + '\t' + str(dictt['actual spread']) + '\t' + str(dictt['last option price']) + '\t' + str(dictt['10 branch binomial equation']) + '\t' + str(dictt['150 branch binomial equation']) + '\t' + str(dictt['option valuation']) + '\t' + str(dictt['Days Til ER']) + '\t'+ str(dictt['StrikeBLow']) + '\t' + str(dictt['ExAfterEarnings']) + '\t' + str(dictt['Premium plus']))
