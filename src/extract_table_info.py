import xlrd
import pandas as pd
from table_extrator_camelot import TableExtractorCamelot
from PyPDF2 import PdfFileReader
from utils import *
import numpy as np
import re
import os
from fuzzywuzzy import fuzz



class TableInfoExtraction:
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

        keywordListFol = os.path.join(os.path.dirname(os.path.realpath(__file__)),  "..","data", "Keywords_BS.XLSX")
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
            self.additionData = []
            self.deductionData = []
            self.creditData = []
            self.additionKeywords = ['Additions',
                         "Deposits",
                         "Refunds",
                         ]
            self.deductionKeywords = ["Deductions",
                                      "Purchases",
                                      "Service Charges and Fees",

                                      ]
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

    def getTableInfo(self, filepath, descriptionCol, depositCol, withdrawCol,edge_tol=85):
        payroll_amounts = []
        cc_amounts = []
        loan_amounts = []
        depositAmount = 0
        averageBalance = 0
        summdata= {}
        summdata["payroll"]={}
        summdata["credit card"]={}
        summdata["loan"]={}
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
                    addition_flag = 0
                    deduction_flag = 0
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
                            for k in self.payroll_keywords:
                                if fuzz.partial_ratio( k.lower(), d1[descriptionCol].lower())>90:
                                    if len(k.split()) >=2:
                                        ratios = [fuzz.partial_ratio(kth.lower(), d1[descriptionCol].lower())>90 for kth in k.split()]
                                        if not re.search(r"\b" + k.lower() + r"\b", d1[descriptionCol].lower()):
                                            if False in ratios:
                                                continue
                                    if fuzz.partial_ratio( k.lower(), d1[descriptionCol].lower())==100:
                                        if not re.search(r"\b" + k.lower() + r"\b", d1[descriptionCol].lower()):
                                            continue
                                    if data_index>0 and len(data.iloc[[data_index-1]]) ==len(data.iloc[[data_index]]) and d1[depositCol]=='' and d1[withdrawCol]=='':
                                        backD1 = d1
                                        d1 = last_data_interated
                                    payroll_amounts.append(self.__format_amount__(d1[depositCol]))
                                    try:
                                        summdata["payroll"][d1[descriptionCol]+" "+backD1[descriptionCol]] = [k,self.__format_amount__(d1[depositCol])]
                                    except:
                                        summdata["payroll"][d1[descriptionCol]] = [k,self.__format_amount__(d1[depositCol])]

                                    break

                            for k in self.cc_keywords:
                                d1[descriptionCol] = d1[descriptionCol].replace("xxxxx", " ")

                                if fuzz.partial_ratio(k.lower(), d1[descriptionCol].lower()) > 90:
                                    if len(k.split()) >=2:
                                        ratios = [fuzz.partial_ratio(kth.lower(), d1[descriptionCol].lower())>90 for kth in k.split()]
                                        if not re.search(r"\b" + k.lower() + r"\b", d1[descriptionCol].lower()):
                                            if False in ratios:
                                                continue
                                    if fuzz.partial_ratio( k.lower(), d1[descriptionCol].lower())==100:
                                        if not re.search(r"\b" + k.lower() + r"\b", d1[descriptionCol].lower()):
                                            continue
                                    if data_index>0 and len(data.iloc[[data_index-1]]) ==len(data.iloc[[data_index]]) and d1[depositCol]=='' and d1[withdrawCol]=='':
                                        backD1 = d1
                                        d1 = last_data_interated
                                    cc_amounts.append(self.__format_amount__(d1[withdrawCol]))
                                    try:
                                        summdata["credit card"][d1[descriptionCol]+" "+backD1[descriptionCol]] = [k,self.__format_amount__(d1[withdrawCol])]
                                    except:
                                        summdata["credit card"][d1[descriptionCol]] = [k,self.__format_amount__(d1[withdrawCol])]

                                    break

                            for k in self.loan_keywords:
                                d1[descriptionCol] = d1[descriptionCol].replace("xxxxx", " ")

                                if fuzz.partial_ratio(k.lower(), d1[descriptionCol].lower()) > 90:
                                    if len(k.split()) >=2:
                                        ratios = [fuzz.partial_ratio(kth.lower(), d1[descriptionCol].lower())>90 for kth in k.split()]
                                        if not re.search(r"\b" + k.lower() + r"\b", d1[descriptionCol].lower()):
                                            if False in ratios:
                                                continue
                                    if fuzz.partial_ratio( k.lower(), d1[descriptionCol].lower())==100:
                                        if not re.search(r"\b" + k.lower() + r"\b", d1[descriptionCol].lower()):
                                            continue
                                    if data_index>0 and len(data.iloc[[data_index-1]]) ==len(data.iloc[[data_index]]) and d1[depositCol]=='' and d1[withdrawCol]=='':
                                        backD1 = d1

                                        d1 = last_data_interated
                                    loan_amounts.append(self.__format_amount__(d1[withdrawCol]))
                                    try:
                                        summdata["loan"][d1[descriptionCol]+" "+backD1[descriptionCol]] = [k,self.__format_amount__(d1[withdrawCol])]
                                    except:
                                        summdata["loan"][d1[descriptionCol]] = [k,self.__format_amount__(d1[withdrawCol])]

                                    break

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


                        except IndexError as e:
                            pass
                        last_data_interated = d1
        except Exception as e:
            raise Exception("Something messed up. Reason: "+str(e))
        payroll_amounts = sum(payroll_amounts)
        cc_amounts = sum(cc_amounts)
        loan_amounts = sum(loan_amounts)
        return payroll_amounts,cc_amounts,loan_amounts, depositAmount, averageBalance,summdata

if __name__=="__main__":
    tableInfoObj = TableInfoExtraction()
    filepath  = r'/Users/prasingh/Prashant/Prashant/CareerBuilder/Extraction/data/BankStatementPDF/0064O00000jc6nkQAA-00P4O00001Jjzq1UAB-joseph_allen_last_60_days_of_b.pdf'
    # filepath  = r'/Users/prasingh/Prashant/Prashant/CareerBuilder/Extraction/data/bankstatements/0060B00000iAQfVQAW-00P4O00001Ic6HpUAJ-bryan_niles_last_60_days_of_ba.pdf'
    # filepath  = r'/Users/prasingh/Prashant/Prashant/CareerBuilder/Extraction/data/BankStatements2/006am4O00000aDJ3zQAG-00P4O00001IbjsmUAB-Pat May BS.pdf'
    filepath  = r'/Users/prasingh/Prashant/Prashant/CareerBuilder/Extraction/data/NEW_BANK/other bank/BB_T BANK/0064O00000k74XZQAY-00P4O00001Jjt9dUAB-Bank Statement.pdf'
    filepath = r"/Users/prasingh/Prashant/Prashant/CareerBuilder/Extraction/data/BS_NT/BS_BOA_Test"
    filepath = r"/Users/prasingh/Prashant/Prashant/CareerBuilder/Extraction/data/Batch4/0064O00000k5zlKQAQ-00P4O00001JkXAtUAN-nichelle_butler_last_60_days_o.pdf"
    payroll_amounts, cc_amounts, loan_amounts, depositAmount, averageDailyBalance, summdata = tableInfoObj.getTableInfo(
        os.path.join(filepath), 1, 2, 2)
    print("payroll: ",payroll_amounts)
    print("credit card: ",cc_amounts)
    print("loan amounts: ",loan_amounts)
    # files = os.listdir(filepath)
    # for i, f in enumerate(files):
    #     if ".pdf" in f:
    #         print(f)
    #         payroll_amounts,cc_amounts,loan_amounts, depositAmount, averageDailyBalance,summdata = tableInfoObj.getTableInfo(os.path.join(filepath,f),1,2,2)
    #         # print("payroll: ",payroll_amounts)
    #         # print("credit card: ",cc_amounts)
    #         # print("loan amounts: ",loan_amounts)
    #         print("deposit amount: ", depositAmount)
    #         print("average amount: ", averageDailyBalance)
    #         print(summdata)

