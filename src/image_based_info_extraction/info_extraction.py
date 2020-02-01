import xlrd
import pandas as pd
import numpy as np
import re
import os


class TableInfoExtractionImage:

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
            return float(amount.strip())
        except:
            return 0


    def getTableInfo(self, data):
        depositAmount = 0
        avgDailyBalance = 0
        try:
            for data_index, d in enumerate(data):
                d1 =re.sub(' +', ' ',d.replace("NEWLINE",""))
                # print(d1)
                try:

                    for k in self.deposits:
                        if  k.lower() in d1.lower():
                            d1 = d1.lower().partition(k.lower())
                            d1 = [i for i in d1 if i.strip()!='']
                            d1 = d1[d1.index(k.lower())+1]
                            d1 = d1.split()[0]

                            if self.checkMoney(d1) == True:
                                depositAmount = self.__format_amount__((d1))
                                break
                    for k in self.average_daily_balance:
                        if  k.lower() in d1.lower():
                            d1 = d1.lower().partition(k.lower())
                            d1 = [i for i in d1 if i.strip()!='']
                            d1 = d1[d1.index(k.lower())+1]
                            d1 = d1.split()[0]

                            if self.checkMoney(d1) == True:
                                avgDailyBalance = self.__format_amount__((d1))
                                break

                except IndexError as e:
                    pass
        except Exception as e:
            raise Exception("Something messed up. Reason: "+str(e))
        return  depositAmount, avgDailyBalance

if __name__=="__main__":
    tableInfoObj = TableInfoExtractionImage()
    filepath  = r'/Users/prasingh/Prashant/Prashant/CareerBuilder/Extraction/data/BS_NT/BS_PNC/3-31-2017 Operating Statement.pdf'
    depositAmount= tableInfoObj.getTableInfo(filepath)
    print("deposit amount: ", depositAmount)

