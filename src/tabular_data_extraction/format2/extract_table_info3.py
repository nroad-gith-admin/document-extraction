import sys, os

curpath = os.path.join(os.path.dirname(os.path.realpath(__file__)))
sys.path.insert(0, curpath)


import xlrd
import pandas as pd
from utils3 import *
import numpy as np
import re
import os
from fuzzywuzzy import fuzz
from get_tabular_data3 import get_tablular_data


class TableInfoExtraction3:

    def __init__(self):
        keywordListFol = os.path.join(os.path.dirname(os.path.realpath(__file__)), ".." ,"..","..","data", "Keywords_BS.XLSX")
        if os.path.isfile(keywordListFol) == False:
            raise Exception("Keyword List file not found in the directory: "+str(keywordListFol))


        try:
            keywordList = (pd.read_excel(keywordListFol)).values.tolist()
        except Exception as e:
            raise Exception("Failed to read the keyword list file. Reason: "+str(e))

        try:
            self.payroll_keywords = [i[0] for i in keywordList if str(i[0]) !='nan']
            self.payroll_keywords = list(set(self.payroll_keywords))
            self.cc_keywords = [i[2] for i in keywordList if str(i[2]) !='nan']
            self.cc_keywords = list(set(self.cc_keywords))

            self.loan_keywords =[str(i[4]) for i in keywordList if str(i[4]) !='nan']
            self.loan_keywords = list(set(self.loan_keywords))

            self.deposits =[str(i[5]).strip() for i in keywordList if str(i[5]) !='nan']
            self.deposits = list(set(self.deposits))

            self.average_daily_balance = [str(i[8]).strip() for i in keywordList if str(i[8]) != 'nan']
            self.average_daily_balance = list(set(self.average_daily_balance))
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



    def __getTableInfo__(self, additionData, deductionData, descriptionCol, depositCol, withdrawCol):
        payroll_amounts = []
        cc_amounts = []
        loan_amounts = []
        depositAmount = 0
        averageBalance = 0
        summdata= {}
        summdata["payroll"]={}
        summdata["credit card"]={}
        summdata["loan"]={}
        data = []
        data.extend(additionData)
        data.extend(deductionData)
        data = pd.DataFrame.from_records(additionData)
        for data_index, d in (data.iterrows()):
            d1 = d
            # print(d1[descriptionCol])
            try:
                for k in self.payroll_keywords:
                    if fuzz.partial_ratio( k.lower(), d1[descriptionCol].lower())>90:
                        if len(k.split()) >=2:
                            ratios = [fuzz.partial_ratio(kth.lower(), d1[descriptionCol].lower())>90 for kth in k.split()]
                            if not re.search(r"\b" + k.lower() + r"\b", d1[descriptionCol].lower()):
                                if False in ratios:
                                    continue
                        if fuzz.partial_ratio(k.lower(), d1[descriptionCol].lower()) == 100:
                            if not re.search(r"\b" + k.lower() + r"\b", d1[descriptionCol].lower()):
                                continue
                        if data_index>0 and len(data.iloc[[data_index-1]]) ==len(data.iloc[[data_index]]) and d1[depositCol]=='' and d1[withdrawCol]=='':
                            backD1 = d1
                            d1 = last_data_interated
                        payroll_amounts.append(self.__format_amount__(d1[depositCol]))
                        try:
                            summdata["payroll"][d1[descriptionCol]+" "+backD1[descriptionCol]+" "+str(data_index)] = [k,self.__format_amount__(d1[depositCol])]
                        except:
                            summdata["payroll"][d1[descriptionCol]+" "+str(data_index)] = [k,self.__format_amount__(d1[depositCol])]

                        break
            except IndexError as e:
                pass
        data = pd.DataFrame.from_records(deductionData)
        for data_index, d in (data.iterrows()):
            d1 = d
            try:
                for k in self.cc_keywords:
                    d1[descriptionCol] = d1[descriptionCol].replace("xxxxx", " ")

                    if fuzz.partial_ratio(k.lower(), d1[descriptionCol].lower()) > 90:
                        if len(k.split()) >=2:
                            ratios = [fuzz.partial_ratio(kth.lower(), d1[descriptionCol].lower())>90 for kth in k.split()]
                            if not re.search(r"\b" + k.lower() + r"\b", d1[descriptionCol].lower()):
                                if False in ratios:
                                    continue
                        if fuzz.partial_ratio(k.lower(), d1[descriptionCol].lower()) == 100:
                            if not re.search(r"\b" + k.lower() + r"\b", d1[descriptionCol].lower()):
                                continue
                        if data_index>0 and len(data.iloc[[data_index-1]]) ==len(data.iloc[[data_index]]) and d1[depositCol]=='' and d1[withdrawCol]=='':
                            backD1 = d1
                            d1 = last_data_interated
                        cc_amounts.append(self.__format_amount__(d1[withdrawCol]))
                        try:
                            summdata["credit card"][d1[descriptionCol]+" "+backD1[descriptionCol]+" "+str(data_index)] = [k,self.__format_amount__(d1[withdrawCol])]
                        except:
                            summdata["credit card"][d1[descriptionCol]+" "+str(data_index)] = [k,self.__format_amount__(d1[withdrawCol])]

                        # print(d1)
                        break

                for k in self.loan_keywords:
                    d1[descriptionCol] = d1[descriptionCol].replace("xxxxx", " ")

                    if fuzz.partial_ratio(k.lower(), d1[descriptionCol].lower()) > 90:
                        if len(k.split()) >=2:
                            ratios = [fuzz.partial_ratio(kth.lower(), d1[descriptionCol].lower())>90 for kth in k.split()]
                            if not re.search(r"\b" + k.lower() + r"\b", d1[descriptionCol].lower()):
                                if False in ratios:
                                    continue
                        if fuzz.partial_ratio(k.lower(), d1[descriptionCol].lower()) == 100:
                            if not re.search(r"\b" + k.lower() + r"\b", d1[descriptionCol].lower()):
                                continue
                        if data_index>0 and len(data.iloc[[data_index-1]]) ==len(data.iloc[[data_index]]) and d1[depositCol]=='' and d1[withdrawCol]=='':
                            backD1 = d1

                            d1 = last_data_interated
                        loan_amounts.append(self.__format_amount__(d1[withdrawCol]))
                        try:
                            summdata["loan"][d1[descriptionCol]+" "+backD1[descriptionCol]+" "+str(data_index)] = [k,self.__format_amount__(d1[withdrawCol])]
                        except:
                            summdata["loan"][d1[descriptionCol]+" "+str(data_index)] = [k,self.__format_amount__(d1[withdrawCol])]

                        break


            except IndexError as e:
                pass





        payroll_amounts = sum(payroll_amounts)
        cc_amounts = sum(cc_amounts)
        loan_amounts = sum(loan_amounts)
        return payroll_amounts,cc_amounts,loan_amounts, summdata

    def getTableInfo(self, filepath, totalCol, dateCol, desCol, depositCol, withdrawCol, totalAmountsCol, isKeywordsPage, headers, additionKeywords, deductionKeywords):
        additionData, deductionData = get_tablular_data(filepath,totalCol, dateCol, desCol, depositCol, withdrawCol, totalAmountsCol, isKeywordsPage, headers, additionKeywords, deductionKeywords)
        # data = pd.DataFrame.from_records(data)
        print(additionData,deductionData)
        payroll_amounts, cc_amounts, loan_amounts, summdata = self.__getTableInfo__(additionData, deductionData, 1, 2, 2)
        return payroll_amounts,cc_amounts,loan_amounts,summdata



if __name__=="__main__":
    tableInfoObj = TableInfoExtraction3()
    additionKeywords, deductionKeywords = ["Transaction history", "Transaction history (continued)"], []
    headers = [["Date", "number", "description", "additions", "subtractions", "balance"],]
    # filepath r""
    # print(os.path.join(filepath, file))
    # filepath = r"/Users/prasingh/Prashant/Prashant/CareerBuilder/Extraction/data/BS_NT/BS_WF/0064O00000k6B5kQAE-00P4O00001JkfySUAR-brett_costa_last_60_days_of_ba.pdf"
    # a, d = get_tablular_data(os.path.join(filepath, file), None, dateCol=0, desCol=2, depositCol=-3, withdrawCol=-2,
    #                          totalAmountsCol=3, isKeywordsPage=True, headers=headers, additionKeywords=additionKeywords,
    #                          deductionKeywords=deductionKeywords)

    # filepath  = r'/Users/prasingh/Prashant/Prashant/CareerBuilder/Extraction/data/BankStatementPDF/0064O00000jc6nkQAA-00P4O00001Jjzq1UAB-joseph_allen_last_60_days_of_b.pdf'
    # filepath  = r'/Users/prasingh/Prashant/Prashant/CareerBuilder/Extraction/data/bankstatements/0060B00000iAQfVQAW-00P4O00001Ic6HpUAJ-bryan_niles_last_60_days_of_ba.pdf'
    # filepath  = r'/Users/prasingh/Prashant/Prashant/CareerBuilder/Extraction/data/BankStatements2/006am4O00000aDJ3zQAG-00P4O00001IbjsmUAB-Pat May BS.pdf'
    # filepath  = r'/Users/prasingh/Prashant/Prashant/CareerBuilder/Extraction/data/BS_NT/BS_WF/0064O00000k6B5kQAE-00P4O00001JkfySUAR-brett_costa_last_60_days_of_ba.pdf'
    filepath  = r'/Users/prasingh/Prashant/Prashant/CareerBuilder/Extraction/data/BS_NT/BS_WF/0064O00000k6B5kQAE-00P4O00001JkfySUAR-brett_costa_last_60_days_of_ba.pdf'
    import pandas as pd
    # df = pd.DataFrame.from_records(data)
    payroll_amounts,cc_amounts,loan_amounts,summdata = tableInfoObj.getTableInfo(filepath, None, dateCol=0, desCol=2, depositCol=-3, withdrawCol=-2,
                             totalAmountsCol=3, isKeywordsPage=True, headers=headers, additionKeywords=additionKeywords,
                             deductionKeywords=deductionKeywords )
    print("payroll: ",payroll_amounts)
    print("credit card: ",cc_amounts)
    print("loan amounts: ",loan_amounts)
    print(summdata)


