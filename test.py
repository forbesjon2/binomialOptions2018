"""---imports---"""
from audioop import mul
from distutils.log import error
from json.tool import main
from queue import Full
import re
from unittest import result
from unittest.mock import call
import urllib.request
import urllib.parse
import numpy as np
import statistics as st
from datetime import date
from datetime import timedelta
import ssl
from td.client import TDClient
ssl._create_default_https_context = ssl._create_unverified_context


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


a = diividend("SPY")
print(a)