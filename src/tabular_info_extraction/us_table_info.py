import sys, os

curpath = os.path.join(os.path.dirname(os.path.realpath(__file__)))
sys.path.insert(0, curpath)

import xlrd
import pandas as pd
from table_extrator_camelot import TableExtractorCamelot
from PyPDF2 import PdfFileReader
from utils import *
import numpy as np
import re
import os
from fuzzywuzzy import fuzz
from extract_electronics import ExtractElectronics
import configparser,os



config_file_loc = os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "..", "config", "bankstatement.cfg")
config_obj = configparser.ConfigParser()



try:
    config_obj.read(config_file_loc)
    account = (config_obj.get("US", "account"))
    routing = (config_obj.get("US", "routing"))
    begBalanceKey = (config_obj.get("US", "begBalanceKey"))
    begBalanceKey = begBalanceKey.split(",")

    endBalanceKey = (config_obj.get("US", "endBalanceKey"))
    endBalanceKey = endBalanceKey.split(",")

    withdrawlKey = (config_obj.get("US", "withdrawlKey"))
    withdrawlKey = withdrawlKey.split(",")

    accountTypeKey = (config_obj.get("US", "accountTypeKey"))
    accountTypeKey = accountTypeKey.split(",")
    # accountTypeKey = [i.replace(":",",") for i in accountTypeKey]

    endDate = (config_obj.get("US", "endDate"))
    endDate = endDate.split(",")

except Exception as e:
    raise Exception("Config file error: " + str(e))

class TableUSInfoExtraction:
    def isDate(self,val):
        val = val.lower()
        if re.search(r"\b" + "jan" + r"\b", val) or \
                re.search(r"\b" + "feb" + r"\b", val) or \
                re.search(r"\b" + "mar" + r"\b", val) or \
                re.search(r"\b" + "apr" + r"\b", val) or \
                re.search(r"\b" + "may" + r"\b", val) or \
                re.search(r"\b" + "jun" + r"\b", val) or \
                re.search(r"\b" + "jul" + r"\b", val) or \
                re.search(r"\b" + "aug" + r"\b", val) or \
                re.search(r"\b" + "sep" + r"\b", val) or \
                re.search(r"\b" + "oct" + r"\b", val) or \
                re.search(r"\b" + "nov" + r"\b", val) or \
                re.search(r"\b" + "dec" + r"\b", val) or \
                re.search(r"\b" + "january" + r"\b", val) or \
                re.search(r"\b" + "february" + r"\b", val) or \
                re.search(r"\b" + "march" + r"\b", val) or \
                re.search(r"\b" + "april" + r"\b", val) or \
                re.search(r"\b" + "may" + r"\b", val) or \
                re.search(r"\b" + "june" + r"\b", val) or \
                re.search(r"\b" + "july" + r"\b", val) or \
                re.search(r"\b" + "august" + r"\b", val) or \
                re.search(r"\b" + "september" + r"\b", val) or \
                re.search(r"\b" + "october" + r"\b", val) or \
                re.search(r"\b" + "november" + r"\b", val) or \
                re.search(r"\b" + "december" + r"\b", val):
            return True

        if "/" in val:
            splitVal = val.split("/")
            splitVal = [i.strip() for i in splitVal if i.strip() != '']
            boolIsDigits = [i.isdigit() for i in splitVal]
            if False in boolIsDigits:
                return False
            return True
        return False
    def __init__(self):

        keywordListFol = os.path.join(os.path.dirname(os.path.realpath(__file__)),  "..","..","data", "Keywords_BS.XLSX")
        if os.path.isfile(keywordListFol) == False:
            raise Exception("Keyword List file not found in the directory: "+str(keywordListFol))

        try:
            self.tableCamelotObj = TableExtractorCamelot()
        except Exception as e:
            raise Exception("Failed to create the TableExtractorCamelot object. Reason: "+str(e))

        try:
            keywordList = (pd.read_excel(keywordListFol)).values.tolist()
        except Exception as e:
            raise Exception("Failed to read the keyword list file. Reason: "+str(e))

        try:


            self.deposits =[str(i[5]).strip() for i in keywordList if str(i[5]) !='nan']
            self.deposits = list(set(self.deposits))

            self.average_daily_balance = [str(i[8]).strip() for i in keywordList if str(i[8]) != 'nan']
            self.average_daily_balance = list(set(self.average_daily_balance))

            self.begBalanceKey = begBalanceKey
            self.endBalanceKey = endBalanceKey
            self.withdrawlKey = withdrawlKey
            self.withdrawlKey = [i.lower().strip() for i in self.withdrawlKey]
            self.endDateKeys = endDate
            self.accountTypeKey = accountTypeKey
            # print(self.average_daily_balance)
        except Exception as e:
            raise Exception("Failed to extract values for payroll_keywords, cc_keywords, loan_keywords. Reason: "+str(e))
    def checkMoney(self, val):
        val = val.replace("$","")

        val = val.replace(".", "")

        val = val.replace(",", "")
        val = val.strip()
        try:
            int(val)
            return True
        except:
            return False

    def __format_amount__(self, amount):
        try:
            amount = amount.replace(",","")

            amount = amount.replace("$", "")
            if "-" in amount:
                amount = amount.replace("-","")
                return 0-float(amount.strip())
            return float(amount.strip())
        except:
            return 0

    def isAmount(self, val):
        val = val.lower()
        val = val.replace("$", '')
        val = val.replace("-", '')
        val = val.replace(",", '')

        if "." in val:
            splitVal = val.split(".")
            splitVal = [i.strip() for i in splitVal if i.strip() != '']
            boolIsDigits = [i.isdigit() for i in splitVal]
            if False in boolIsDigits:
                return False
            return True
        return False

    def extractAmount(self, val):
        val = val.lower()
        val = val.replace("$", '')
        val = val.replace("-", '')
        val = val.replace(",", '')

        return val

    def extract_amount_key(self,dataRow, keywords ):
        dataRow = dataRow.lower()
        for keys in keywords:
            keyword = keys.lower()
            # if re.search(r"\b" + keyword.lower() + r"\b", dataRow.lower()):
            if dataRow.lower().startswith(keyword.lower()):
                before_keyword, keyword, after_keyword = dataRow.partition(keyword)
                after_keyword = after_keyword.split()
                amounts = [self.__format_amount__(i) for i in after_keyword if self.isAmount(i) == True]
                if len(amounts)>0:
                    return amounts[0], keyword

        return None,None


    def getTableInfo(self, filepath, descriptionCol, depositCol, withdrawCol,edge_tol=85):
        depositAmount = 0
        averageBalance = 0
        begBalance = 0
        endBalance = 0
        endDate = ""
        withdrawlBalances = []
        accountType = ""
        self.extractElecObj = ExtractElectronics(filepath)
        numPage = self.extractElecObj.num_page()
        data = []
        for i in list(range(numPage)):
            data.extend(self.extractElecObj.read_page(pageNums=[i, ], typeOut='blocks')[0])

        data =  [str(i[-3]) for i in data if str(i[-3]).strip() != '']
        newData = []
        for d in data:
            newData.extend(d.split("\n"))
        data = newData
        lastExtractedVal = None
        for data_index, dataRow in enumerate(data):
            if depositAmount == 0:
                extactedVal, foundKey = self.extract_amount_key(dataRow, self.deposits)
                if extactedVal!=None:
                    depositAmount = extactedVal
            if begBalance == 0:
                extactedVal,foundKey = self.extract_amount_key(dataRow, self.begBalanceKey)
                if extactedVal != None:
                    begBalance = extactedVal
            if endBalance == 0:
                extactedVal,foundKey = self.extract_amount_key(dataRow, self.endBalanceKey)
                if extactedVal != None:
                    endBalance = extactedVal

            if averageBalance == 0:
                extactedVal,foundKey = self.extract_amount_key(dataRow, self.average_daily_balance)
                if extactedVal != None:
                    averageBalance = extactedVal

            # if endBalance == 0:
            extactedVal,foundKey = self.extract_amount_key(dataRow, self.withdrawlKey)
            if extactedVal!= None and lastExtractedVal ==None:

                withdrawlBalances.append(extactedVal)
                lastExtractedVal = foundKey
            elif extactedVal!=None and lastExtractedVal != None and lastExtractedVal in self.withdrawlKey:
                withdrawlBalances.append(extactedVal)
                lastExtractedVal = foundKey
            elif lastExtractedVal!=None:
                lastExtractedVal = foundKey


            if endDate=='':
                for keys in self.endDateKeys:
                    if keys in dataRow:
                        enddateSplitted = dataRow.split(keys)
                        endDate = enddateSplitted[-1]
                        endDate = endDate.split("$")
                        endDate = endDate[0]


            if accountType=='':
                for keys in self.accountTypeKey:
                    if keys in dataRow:
                        accountType = dataRow.replace(keys,"").strip()
                        # splittedWords = dataRow.split(keys)
                        # splittedWords = [i for i in splittedWords if i.strip() != '']
                        # accountType = splittedWords[0]

        withdrawlBalances = sum(withdrawlBalances)
        return depositAmount, averageBalance, begBalance, endBalance, withdrawlBalances, endDate, accountType

if __name__=="__main__":
    tableInfoObj = TableUSInfoExtraction()
    filepath  = r'/Users/prasingh/Prashant/Prashant/CareerBuilder/Extraction/data/BS_NT/BS_US/0064O00000jteKqQAI-00P4O00001JkXBcUAN-__last_60_days_of_bank_stateme.pdf'
    # filepath  = r'/Users/prasingh/Prashant/Prashant/CareerBuilder/Extraction/data/bankstatements/0060B00000iAQfVQAW-00P4O00001Ic6HpUAJ-bryan_niles_last_60_days_of_ba.pdf'
    # filepath  = r'/Users/prasingh/Prashant/Prashant/CareerBuilder/Extraction/data/BankStatements2/006am4O00000aDJ3zQAG-00P4O00001IbjsmUAB-Pat May BS.pdf'
    # filepath  = r'/Users/prasingh/Prashant/Prashant/CareerBuilder/Extraction/data/NEW_BANK/other bank/BB_T BANK/0064O00000k74XZQAY-00P4O00001Jjt9dUAB-Bank Statement.pdf'
    # filepath = r"/Users/prasingh/Prashant/Prashant/CareerBuilder/Extraction/data/BS_NT/BS_BOA_Test"
    # filepath = r"/Users/prasingh/Prashant/Prashant/CareerBuilder/Extraction/data/BS_NT/BS_JPMC/0064O00000k8zFYQAY-00P4O00001KC3bdUAD-__last_60_days_of_bank_stateme.pdf"
    # depositAmount, averageDailyBalance, beg, end, withdraw, endDate, accounttype  = tableInfoObj.getTableInfo(
    #     os.path.join(filepath), 1, 2, 2)
    # print("beg amounts: ", beg)
    # print("end amounts: ", end)
    # print("with amounts: ", withdraw)
    # print("end date: ", endDate)
    # print("accounttype: ", accounttype)
    # print("depositAmount: ", depositAmount)
    # print("averageDailyBalance: ", averageDailyBalance)


    folderpath = r"/Users/prasingh/Prashant/Prashant/CareerBuilder/Extraction/data/BS_NT/BS_US_Test"

    for file in os.listdir(folderpath):
        if ".pdf" in file:
            print(file)
            filepath = os.path.join(folderpath, file)
            depositAmount, averageDailyBalance, beg, end, withdraw, endDate,accounttype = tableInfoObj.getTableInfo(
                os.path.join(filepath), 1, 2, 2)
            print("beg amounts: ", beg)
            print("end amounts: ", end)
            print("with amounts: ", withdraw)
            print("end date: ", endDate)
            print("accounttype: ", accounttype)
            print("depositAmount: ", depositAmount)
            print("averageDailyBalance: ", averageDailyBalance)
            print("-------------------------")
    #         # break