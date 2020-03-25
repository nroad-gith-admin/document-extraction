import sys, os

curpath = os.path.join(os.path.dirname(os.path.realpath(__file__)))
sys.path.insert(0, curpath)

import pandas as pd
from table_extrator_camelot import TableExtractorCamelot
from PyPDF2 import PdfFileReader
from utils import *
import numpy as np
import re
import os
from fuzzywuzzy import fuzz
import configparser,os



config_file_loc = os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "..", "config", "bankstatement.cfg")
config_obj = configparser.ConfigParser()



try:
    config_obj.read(config_file_loc)
    account = (config_obj.get("PNC", "account"))
    routing = (config_obj.get("PNC", "routing"))
    begBalanceKey = (config_obj.get("PNC", "begBalanceKey"))
    begBalanceKey = begBalanceKey.split(",")

    endBalanceKey = (config_obj.get("PNC", "endBalanceKey"))
    endBalanceKey = endBalanceKey.split(",")

    withdrawlKey = (config_obj.get("PNC", "withdrawlKey"))
    withdrawlKey = withdrawlKey.split(",")

    accountTypeKey = (config_obj.get("PNC", "accountTypeKey"))
    accountTypeKey = accountTypeKey.split(",")
    accountTypeKey = [i.replace(":",",") for i in accountTypeKey]

    endDate = (config_obj.get("PNC", "endDate"))
    endDate = endDate.split(",")
    endDate = [i.replace(":",",") for i in endDate]

except Exception as e:
    raise Exception("Config file error: " + str(e))

class TablePNCInfoExtraction:

    def __init__(self):

        keywordListFol = os.path.join(os.path.dirname(os.path.realpath(__file__)), ".." ,"..","data", "Keywords_BS.XLSX")
        if os.path.isfile(keywordListFol) == False:
            raise Exception("Keyword List file not found in the directory: "+str(keywordListFol))



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
            self.accountTypeKey = accountTypeKey
            self.endDateKeys = endDate
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

    def getTableInfo(self, data):
        depositAmount, avgDailyBalance, begBalance, endBalance, withdrawAmounts, endDate, accounttype=0,0,0,0,0,None,None
        withdrawlBalances = 0
        accountType = {}
        try:
            for data_index, d in enumerate(data):
                d1Main =re.sub(' +', ' ',d.replace("NEWLINE",""))
                # print(d1)
                d1 = d1Main
                try:

                    for k in self.deposits:
                        d1 = d1Main
                        if  k.lower() in d1.lower():
                            d1 = d1.lower().partition(k.lower())
                            d1 = [i for i in d1 if i.strip()!='']
                            d1 = d1[d1.index(k.lower())+1]
                            d1 = d1.split()[0]

                            if self.checkMoney(d1) == True:
                                depositAmount = self.__format_amount__((d1))
                                break
                    for k in self.average_daily_balance:
                        d1 = d1Main
                        if  k.lower() in d1.lower():
                            d1 = d1.lower().partition(k.lower())
                            d1 = [i for i in d1 if i.strip()!='']
                            d1 = d1[d1.index(k.lower())+1]
                            d1 = d1.split()[0]

                            if self.checkMoney(d1) == True:
                                avgDailyBalance = self.__format_amount__((d1))
                                break
                    if begBalance == 0:
                        d1 = d1Main
                        for k in self.begBalanceKey:
                            if k.lower() in d1.lower():
                                d1 = d1.lower().partition(k.lower())
                                d1 = [i for i in d1 if i.strip() != '']
                                d1 = d1[d1.index(k.lower()) + 1]
                                d1 = d1.split()[0]

                                if self.checkMoney(d1) == True:
                                    begBalance = self.__format_amount__((d1))
                                    break
                    if endBalance == 0:
                        d1 = d1Main
                        for k in self.endBalanceKey:
                            if k.lower() in d1.lower():

                                d1 = d1.lower().partition(k.lower())
                                d1 = [i for i in d1 if i.strip() != '']
                                d1 = d1[d1.index(k.lower()) + 1]
                                d1 = d1.split()[0]

                                if self.checkMoney(d1) == True:
                                    endBalance = self.__format_amount__((d1))
                                    break
                    # if accountType == "":
                    w = d1
                    for accountTypeKeys in self.accountTypeKey:
                        accountTypeKeys  = accountTypeKeys.split(",")
                        accountTypeVal = re.search(accountTypeKeys[0] + "(.*)" + accountTypeKeys[1], w)
                        if accountTypeVal !=None:
                            if len(accountTypeVal.group(1).strip().split()) < 3:
                                try:
                                    accountType[accountTypeVal.group(1).strip()] = accountType[accountTypeVal.group(
                                        1).strip()] + 1
                                except:
                                    accountType[accountTypeVal.group(1).strip()] = 1
                                break

                    if endDate==None:
                        for endDatekey in self.endDateKeys:
                            if endDatekey.lower() not in d1.lower():
                                break
                        else:
                            endDate = d1.split('to')[-1].split()[0]
                    if withdrawlBalances == 0:
                        d1 = d1Main
                        for k in self.withdrawlKey:
                            if k.lower() in d1.lower():

                                d1 = d1.lower().partition(k.lower())
                                d1 = [i for i in d1 if i.strip() != '']
                                d1 = d1[d1.index(k.lower()) + 1]
                                d1 = d1.split()[0]

                                if self.checkMoney(d1) == True:
                                    withdrawlBalances = self.__format_amount__((d1))
                                    break

                except IndexError as e:
                    print(e)

        except Exception as e:
            raise Exception("Something messed up. Reason: "+str(e))

        # withdrawlBalances = sum(withdrawlBalances)
        return  depositAmount, avgDailyBalance, begBalance, endBalance, withdrawlBalances, endDate,", ".join(accountType.keys())

if __name__=="__main__":
    tableInfoObj = TablePNCInfoExtraction()
    # filepath  = r'/Users/prasingh/Prashant/Prashant/CareerBuilder/Extraction/data/BS_NT/BS_PNC/0064O00000kBOB5QAO-00P4O00001JkMbIUAV-shawn_frick_last_60_days_of_ba.pdf'
    data = ['@© PNC BANK', 'Business Checking NEWLINE PNC Bank', 'For the Period 06/29/2019 to 07/31/2019', 'Primary Account Number: 46-4469-0797 NEWLINE  NEWLINE Page 1 of 7 NEWLINE  NEWLINE Number of enclosures: 0 NEWLINE  NEWLINE Tt For 24-hour banking sign on to NEWLINE  NEWLINE g PNC Bank Online Banking on pnc.com NEWLINE FREE Online Bill Pay NEWLINE For customer service call 1-877-BUS-BNKG NEWLINE Monday - Friday: 7 AM - 10 PM ET NEWLINE Saturday & Sunday: 8 AM - 5 PM ET', 'MOSQUITO AUTHORITY NEWLINE 176 LOGAN ST 117 NEWLINE NOBLESVILLE IN 46060-1437', 'Para servicio en espanol, 1-877-BUS-BNKG NEWLINE Moving? Please contact your local branch NEWLINE ® write to: Customer Service NEWLINE  NEWLINE PO Box 609 NEWLINE  NEWLINE Pittsburgh, PA 15230-9738 NEWLINE 2 Visit us at PNC.com/smallbusiness NEWLINE a TDD terminal: 1-800-531-1648 NEWLINE  NEWLINE For hearing impaired clients only', "Watch Where You Click NEWLINE  NEWLINE Be sure the emails, texts and phone calls you receive are from a trusted source and do not give out personal NEWLINE information, such as credit card numbers, Social Security numbers or other banking details, unless you have NEWLINE verified the sender. If you are unsure, contact PNC directly by typing www.pnc.com into your Internet browser NEWLINE or call PNC using a phone number provided on the www.pnc.com website. DO NOT use contact information NEWLINE contained in the suspect email or text. If you suspect you've received a fraudulent text message that appears NEWLINE to be from PNC, take a screen shot of the text message on your mobile phone and forward it to PNC Abuse NEWLINE (abuse@pnc.com). NEWLINE  NEWLINE Business Checking Summary Mesa Pan hay NEWLINE  NEWLINE Account number: 46-4469-0797", 'Overdraft Protection has not been established for this account. NEWLINE Please contact us if you would like to set up this service.', 'Balance Summary', 'Beginning NEWLINE balance NEWLINE 6,552.54', 'Deposits and NEWLINE other additions NEWLINE 9,330.00', 'Checks and other NEWLINE deductions NEWLINE 10,708.18 NEWLINE Average ledger NEWLINE balance NEWLINE 5,855.06', 'Ending NEWLINE  NEWLINE balance NEWLINE 5,174.36 NEWLINE Average collected NEWLINE balance NEWLINE 5,829.94', 'Deposits and Other Additions NEWLINE Description NEWLINE  NEWLINE Deposits NEWLINE  NEWLINE ATM Deposits and Additions NEWLINE ACH Additions', 'Checks and Other Deductions NEWLINE Amount Description NEWLINE 247.00 | Checks NEWLINE 2,231.00 | Debit Card Purchases NEWLINE 6,852.00 | POS Purchases NEWLINE ATM/Misc. Debit Card NEWLINE Transactions NEWLINE ACH Deductions NEWLINE Service Charges and Fees NEWLINE Other Deductions NEWLINE 9,330.00 | Total', 'Items NEWLINE 1 NEWLINE 12 NEWLINE 21', 'Items NEWLINE 1 NEWLINE 47 NEWLINE 25 NEWLINE 7', 'Amount NEWLINE 20.00 NEWLINE 1,235.19 NEWLINE 1,137.35 NEWLINE 1,071.17', '3,242.47 NEWLINE 2.00 NEWLINE 4,000.00 NEWLINE 10,708.18', '. . NEWLINE Business Checking NEWLINE g For 24-hour account information, sign-on to NEWLINE  NEWLINE pnc.com/mybusiness/', 'For the Period 06/29/2019 to 07/31/2019 NEWLINE Mosquito Authority NEWLINE  NEWLINE Primary Account Number: 46-4469-0797 NEWLINE Page 2 of 7', 'Business Checking Account Number: 46-4469-0797 - continued NEWLINE Daily Balance NEWLINE  NEWLINE Date Ledger balance Date NEWLINE  NEWLINE 06/29 6,552.54 07/11 NEWLINE  NEWLINE 07/01 7,460.97 07/12 NEWLINE  NEWLINE 07/02 6,340.11 07/15 NEWLINE  NEWLINE 07/03 5,954.09 07/17 NEWLINE  NEWLINE 07/05 6,063.37 07/18 NEWLINE  NEWLINE 07/08 4,698.46 07/19 NEWLINE  NEWLINE 07/10 4,898.25 07/22 NEWLINE Activity Detail NEWLINE Deposited Other Amore NEWLINE Deposits NEWLINE  NEWLINE Date Transaction NEWLINE posted Amount description NEWLINE  NEWLINE 07/11 247.00 Deposit NEWLINE  NEWLINE ATM Deposits and Additions NEWLINE  NEWLINE Date Transaction NEWLINE posted Amount description NEWLINE 07/01 259.00 ATM Deposit 3 NEWLINE 07/01 134.00 ATM Deposit 3 NEWLINE 07/08 130.00 ATM Deposit 3 NEWLINE 07/08 79.00 ATM Deposit 3 NEWLINE 07/10 65.00 ATM Deposit 3 NEWLINE 07/12 195.00 ATM Deposit 3 NEWLINE 07/15 159.00 ATM Deposit NEWLINE 07/18 258.00 ATM Deposit 3 NEWLINE 07/19 200.00 ATM Deposit 3 NEWLINE 07/25 374.00 ATM Deposit 3 NEWLINE 07/29 179.00 ATM Deposit 3 NEWLINE 07/31 199.00 ATM Deposit 3 NEWLINE ACH Additions NEWLINE  NEWLINE Date Transaction NEWLINE posted Amount description NEWLINE  NEWLINE 07/01 377.00 Corporate ACI', 'Date NEWLINE  NEWLINE 07/23 NEWLINE 07/24 NEWLINE 07/25 NEWLINE 07/26 NEWLINE 07/29 NEWLINE 07/30 NEWLINE 07/31', 'Ledger balance NEWLINE 5,394.25 NEWLINE 5,528.83 NEWLINE 6,157.48 NEWLINE 6,635.04 NEWLINE 5,871.88 NEWLINE 6,006.33 NEWLINE 5,649.74', 'Ledger balance NEWLINE 5,325.77 NEWLINE 5,232.33 NEWLINE 5,600.56 NEWLINE 5,823.98 NEWLINE 6,375.39 NEWLINE 6,265.77 NEWLINE 5,174.36', 'Transaction NEWLINE  NEWLINE description NEWLINE  NEWLINE Deposit NEWLINE  NEWLINE Transaction NEWLINE  NEWLINE description NEWLINE  NEWLINE ATM Deposit 3267 State Rd 3 Westfield In NEWLINE ATM Deposit 300 Sheridan Ro Noblesville NEWLINE ATM Deposit 300 Sheridan Ro Noblesville NEWLINE ATM Deposit 300 Sheridan Ro Noblesville NEWLINE ATM Deposit 300 Sheridan Ro Noblesville NEWLINE ATM Deposit 300 Sheridan Ro Noblesville NEWLINE ATM Deposit NEWLINE  NEWLINE ATM Deposit 300 Sheridan Ro Noblesville NEWLINE ATM Deposit 300 Sheridan Ro Noblesville NEWLINE ATM Deposit 300 Sheridan Ro Noblesville NEWLINE ATM Deposit 300 Sheridan Ro Noblesville NEWLINE ATM Deposit 300 Sheridan Ro Noblesville', 'Reference NEWLINE number NEWLINE 031779927', 'Reference NEWLINE  NEWLINE number NEWLINE  NEWLINE 83544954 PNC PX2084 NEWLINE 83695639 PNC PJ1643 NEWLINE 83260761 PNC PJ1643 NEWLINE 84137195 PNC PJ1643 NEWLINE 85685071 PNC PJ1643 NEWLINE 86901557 PNC PJ1643 NEWLINE 005319 PNC PJ1643 NEWLINE 86448644 PNC PJ1643 NEWLINE 83108048 PNC PJ1643 NEWLINE 86393807 PNC PJ1643 NEWLINE 83633246 PNC PJ1643 NEWLINE 85810815 PNC PJ1643', 'Transaction NEWLINE  NEWLINE description NEWLINE  NEWLINE Corporate ACH Settlement NEWLINE Bankcard 628070000452473 NEWLINE Corporate ACH Settlement NEWLINE Bankcard 628070000452473 NEWLINE Corporate ACH Settlement NEWLINE Bankcard 628070000452473 NEWLINE Corporate ACH Settlement NEWLINE Bankcard 628070000452473 NEWLINE Corporate ACH Settlement NEWLINE Bankcard 628070000452473 NEWLINE Corporate ACH Settlement NEWLINE Bankcard 628070000452473 NEWLINE Corporate ACH Settlement NEWLINE Bankcard 628070000452473 NEWLINE Corporate ACH Settlement NEWLINE Bankcard 628070000452473', 'Reference NEWLINE number NEWLINE 00019182903168985', 'O7/0t NEWLINE 07/01 NEWLINE 07/03 NEWLINE 07/05 NEWLINE 07/08', '144.00 NEWLINE 124.00 NEWLINE 357.00 NEWLINE 303.00 NEWLINE 178.00', '00019182903334857 NEWLINE 00019182903156306 NEWLINE 00019184901983479 NEWLINE 00019186905219958 NEWLINE 00019189908946330 NEWLINE 00019189909078135 NEWLINE 00019191904942387', '07/08 NEWLINE 07/10', '59.00 NEWLINE 200.00', 'ACH Additions continued on next page']

    depositAmount, averageBalance, begBalance, endBalance, withdrawlBalances, endDate, accountType = tableInfoObj.getTableInfo(data)
    print("deposit amount: ", depositAmount)
    print("avgDailyBalance: ", averageBalance)
    print("begBalance: ", begBalance)
    print("endBalance: ", endBalance)
    print("withdrawlBalances: ", withdrawlBalances)
    print("endDate: ", endDate)
    print("accountType: ", accountType)

