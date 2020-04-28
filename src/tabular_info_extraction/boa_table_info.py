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
import configparser,os



config_file_loc = os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "..", "config", "bankstatement.cfg")
config_obj = configparser.ConfigParser()



try:
    config_obj.read(config_file_loc)
    account = (config_obj.get("BOA", "account"))
    routing = (config_obj.get("BOA", "routing"))
    begBalanceKey = (config_obj.get("BOA", "begBalanceKey"))
    begBalanceKey = begBalanceKey.split(",")

    endBalanceKey = (config_obj.get("BOA", "endBalanceKey"))
    endBalanceKey = endBalanceKey.split(",")

    withdrawlKey = (config_obj.get("BOA", "withdrawlKey"))
    withdrawlKey = withdrawlKey.split(",")

    accountTypeKey = (config_obj.get("BOA", "accountTypeKey"))
    accountTypeKey = accountTypeKey.split(",")
    # accountTypeKey = [i.replace(":",",") for i in accountTypeKey]
    accountTypeKey.sort(key=lambda x:len(x),reverse=True)
except Exception as e:
    raise Exception("Config file error: " + str(e))


class TableBOAInfoExtraction:
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

            self.yearFormat = {"jan":1,"feb":2,"mar":3,"apr":4,"may":5,"june":6,"july":7,"aug":8,"sep":9,"oct":10,"nov":11,"dec":12}
            self.deposits =[str(i[5]).strip() for i in keywordList if str(i[5]) !='nan']
            self.deposits = list(set(self.deposits))

            self.average_daily_balance = [str(i[8]).strip() for i in keywordList if str(i[8]) != 'nan']
            self.average_daily_balance = list(set(self.average_daily_balance))

            self.begBalanceKey = begBalanceKey
            self.endBalanceKey = endBalanceKey
            self.withdrawlKey = withdrawlKey
            self.accountTypeKey = accountTypeKey
            # print(self.payroll_keywords)
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

    def __format__date(self, date):
        year = date.split(",")[-1]
        for years in range(2010,2030):
            if str(years) in date:
                year = years
                break
        monthDay = date.split(",")[0]
        monthDay = monthDay.strip()
        month = monthDay.split()[0]
        day = monthDay.split()[-1]
        for k, v in self.yearFormat.items():
            if k in month.lower():
                month = v
                break

        return str(str(month)+"/"+str(day)+"/"+str(year))

    def getTableInfo(self, filepath, descriptionCol, depositCol, withdrawCol,edge_tol=85):
        depositAmount = 0
        averageBalance = 0
        begBalance = 0
        endBalance = 0
        endDate = ""
        withdrawlBalances = []
        accountType = ""

        try:
            pdf = PdfFileReader(open(filepath, 'rb'))
        except Exception as e:
            raise Exception("Failed to read the file: "+str(filepath)+" Reason: "+str(e))
        num_pages = pdf.getNumPages()
        try:
            for page in range(1, num_pages + 1):
                try:
                    tables = self.tableCamelotObj.extract_table(filepath, str(page),edge_tol)
                except:
                    continue

                tables = list(set(tables))
                if len(tables) > 1:
                    new_t = []
                    removed_table = []
                    done_comparing_index = {}
                    for i in range(len(tables)):
                        for j in range(len(tables)):
                            report1 = tables[i].parsing_report
                            report2 = tables[j].parsing_report
                            if report1["accuracy"] != 100 and report2["accuracy"] != 100:
                                if i != j:
                                    try:
                                        if j in done_comparing_index[i]:
                                            pass
                                        else:
                                            raise Exception()
                                    except:
                                        try:
                                            done_comparing_index[j].append(i)
                                        except:
                                            done_comparing_index[j] = []
                                            done_comparing_index[j].append(i)

                                        if check_table_inside_table(tables[i], tables[j]) == True:

                                            removed_table.append(tables[i])

                                        elif check_table_inside_table(tables[j], tables[i]) == True:

                                            removed_table.append(tables[j])
                    for i in tables:
                        if i not in removed_table:
                            new_t.append(i)
                    tables = list(set(new_t))

                for table_i in range(len(tables)):
                    data = tables[table_i].df
                    data = data.applymap(clean_pandas)
                    d = data.replace(r'^\s*$', np.nan, regex=True)
                    d = d.isnull().all()
                    ind = d.index[d].tolist()
                    if len(ind) > 0:
                        data = data.drop(ind, axis=1)
                    report = tables[table_i].parsing_report

                    last_data_interated = None
                    for data_index, d in data.iterrows():
                        d1 = df_to_list(d)
                        try:


                            if averageBalance==0:
                                for k in self.average_daily_balance:
                                    for dii, di in enumerate(d):
                                        if re.search(r"\b" + k.lower() + r"\b", di.lower()):
                                            try:
                                                averageBalanceD1 = [i.lower().strip() for i in d1 if i.strip() != '']
                                                averageBalance = averageBalanceD1[averageBalanceD1.index(k.lower())+1]
                                                break
                                            except:
                                                pass
                            if depositAmount==0:
                                for k in self.deposits:
                                    if page ==1 or page==2 or page==3:
                                        for d_i in d1:
                                            if  k.lower() == d_i.lower():
                                                d1 = [d1i.lower() for d1i in d1 if d1i.strip()!='']
                                                ind = d1.index(k.lower())
                                                if len(d1)> ind+1:
                                                    if self.checkMoney(d1[ind+1]) == True:
                                                        depositAmount = self.__format_amount__((d1[ind+1]))

                                                break

                            if begBalance == 0:
                                for k in self.begBalanceKey:
                                    if k.lower() in " ".join(d1).lower():
                                        d1 = [d1i.lower() for d1i in d1 if d1i.strip() != '']
                                        words = " ".join(d1).split()
                                        words = [self.__format_amount__(i) for i in words if self.isAmount(i)==True]
                                        begBalance = words[0]
                                        # print(begBalance)
                            if endBalance==0:
                                for k in self.endBalanceKey:
                                    if k.lower() in " ".join(d1).lower():
                                        d1 = [d1i.lower() for d1i in d1 if d1i.strip() != '']
                                        words = " ".join(d1).split()
                                        words = [i for i in words if self.isAmount(i)==True]
                                        endBalance = self.__format_amount__(words[0])
                                        endDate = " ".join(d1).lower().replace(k.lower(),"").replace(words[0],"").strip()
                                        endDate = self.__format__date(endDate)
                            # if accountType == "":
                            w = " ".join(d1)
                            for accountTypeKeys in self.accountTypeKey:
                                if accountTypeKeys.lower() in " ".join(d1).lower():
                                    # splittedWords = dataRow.split(keys)
                                    # splittedWords = [i for i in splittedWords if i.strip() != '']
                                    accountType = accountTypeKeys
                                    break
                                # accountTypeKeys = accountTypeKeys.split(",")
                                # flags = [accountKey in w for accountKey in accountTypeKeys]
                                # if False not in flags:
                                #     accountTypeVal = re.search(accountTypeKeys[0] + "(.*)" + accountTypeKeys[1], w)
                                #     if accountTypeVal!=None:
                                #         if len(accountTypeVal.group(1).strip().split())<3:
                                #             try:
                                #                 accountType[accountTypeVal.group(1).strip()] = accountType[accountTypeVal.group(1).strip()]+1
                                #             except:
                                #                 accountType[accountTypeVal.group(1).strip()] = 1
                                #             break

                            for k in self.withdrawlKey:
                                if " ".join(d1).lower().startswith(k.lower()):
                                    d1 = [d1i.lower() for d1i in d1 if d1i.strip() != '']
                                    words = " ".join(d1).split()
                                    words = [self.__format_amount__(i) for i in words if self.isAmount(i)==True]
                                    withdrawlBalances.append(words[0])

                        except IndexError as e:
                            pass

                        last_data_interated = d1

        except Exception as e:
            raise Exception("Something messed up. Reason: "+str(e))

        withdrawlBalances = sum(withdrawlBalances)
        withdrawlBalances = float(str(withdrawlBalances).replace("-","").strip())
        return depositAmount, averageBalance, begBalance, endBalance, withdrawlBalances, endDate,accountType

if __name__=="__main__":
    tableInfoObj = TableBOAInfoExtraction()
    filepath  = r'/Users/prasingh/Prashant/Prashant/CareerBuilder/Extraction/data/BankStatementPDF/0064O00000jc6nkQAA-00P4O00001Jjzq1UAB-joseph_allen_last_60_days_of_b.pdf'
    # filepath  = r'/Users/prasingh/Prashant/Prashant/CareerBuilder/Extraction/data/bankstatements/0060B00000iAQfVQAW-00P4O00001Ic6HpUAJ-bryan_niles_last_60_days_of_ba.pdf'
    # filepath  = r'/Users/prasingh/Prashant/Prashant/CareerBuilder/Extraction/data/BankStatements2/006am4O00000aDJ3zQAG-00P4O00001IbjsmUAB-Pat May BS.pdf'
    filepath  = r'/Users/prasingh/Prashant/Prashant/CareerBuilder/Extraction/data/NEW_BANK/other bank/BB_T BANK/0064O00000k74XZQAY-00P4O00001Jjt9dUAB-Bank Statement.pdf'
    filepath = r"/Users/prasingh/Prashant/Prashant/CareerBuilder/Extraction/data/BS_NT/BS_BOA_Test"
    filepath = r"/Users/prasingh/Prashant/Prashant/CareerBuilder/Extraction/data/BS_Batch1/0064O00000jtGT2QAM-00P4O00001IbVZpUAN-eStmt_2019-08-30.pdf"
    depositAmount, averageDailyBalance, beg, end, withdraw, endDate, accounttype = tableInfoObj.getTableInfo(
        filepath, 1, 2, 2)
    print("beg amounts: ", beg)
    print("end amounts: ", end)
    print("with amounts: ", withdraw)
    print("end date: ", endDate)
    print("accounttype: ", accounttype)
    print("depositAmount: ", depositAmount)
    print("averageDailyBalance: ", averageDailyBalance)
    print("-------------------------")


    # folderpath = r"/Users/prasingh/Prashant/Prashant/CareerBuilder/Extraction/data/BS_NT/BS_BOA/"
    #
    # for file in os.listdir(folderpath):
    #     print(file)
    #     filepath = os.path.join(folderpath, file)
    #     depositAmount, averageDailyBalance, beg, end, withdraw, endDate,accounttype = tableInfoObj.getTableInfo(
    #         os.path.join(filepath), 1, 2, 2)
    #     print("beg amounts: ", beg)
    #     print("end amounts: ", end)
    #     print("with amounts: ", withdraw)
    #     print("end date: ", endDate)
    #     print("accounttype: ", accounttype)
    #     print("depositAmount: ", depositAmount)
    #     print("averageDailyBalance: ", averageDailyBalance)
    #     print("-------------------------")
        # break