import re

class get_stock_list():
    def stock_list_calc(self):
        if self == 'Monday':
            num = 1
        elif self == 'Tuesday':
            num = 2
        elif self == 'Wednesday':
            num = 3
        elif self == 'Thursday':
            num = 4
        else:
            num = 0

        filee = open("zacks_custom_screen.csv", 'r')
        filee = filee.read()

        mainList= re.findall(r'\"(.*?)\"YES\"', filee)
        writeMode = 'a'
        stockList = []
        if num == 1:
            writeMode = 'w+'
            stockList = re.findall('\"([A-C][A-Z]?[A-Z]?[A-Z]?[A-Z]?[A-Z]?)\"', str(mainList))
        elif num == 2:
            stockList = re.findall('\"([D-I][A-Z]?[A-Z]?[A-Z]?[A-Z]?[A-Z]?)\"', str(mainList))
        elif num == 3:
            stockList= re.findall('\"([J-Q][A-Z]?[A-Z]?[A-Z]?[A-Z]?[A-Z]?)\"', str(mainList))
        elif num == 4:
            stockList = re.findall('\"([A-Z][A-Z]?[A-Z]?[A-Z]?[A-Z]?[A-Z]?)\"', str(mainList))
        else:
            writeMode = 'na'
            pass
        return stockList, writeMode