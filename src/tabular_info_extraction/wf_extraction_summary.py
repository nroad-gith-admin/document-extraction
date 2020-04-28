import re, os
import pandas as pd
from fuzzywuzzy import fuzz, process
from string import punctuation
from nltk import ngrams

payrollkeywords = ['Direct Dep','Dir Dep']
checkkeywords = ['CREDIT CARDS Bill Payment', "Credit Card Bill Payment"]


class WFExtractSum:
    def __init__(self):
        keywordListFol = os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "..","data", "Keywords_BS.XLSX")
        if os.path.isfile(keywordListFol) == False:
            raise Exception("Keyword List file not found in the directory: " + str(keywordListFol))



        try:
            keywordList = (pd.read_excel(keywordListFol)).values.tolist()
        except Exception as e:
            raise Exception("Failed to read the keyword list file. Reason: " + str(e))

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
            self.payroll_keywords = [i[0] for i in keywordList if str(i[0]) != 'nan']
            self.payroll_keywords = list(set(self.payroll_keywords))
            self.cc_keywords = [i[2] for i in keywordList if str(i[2]) != 'nan']
            self.cc_keywords = list(set(self.cc_keywords))

            self.loan_keywords = [str(i[4]) for i in keywordList if str(i[4]) != 'nan']
            self.loan_keywords = list(set(self.loan_keywords))

            self.deposits = [str(i[5]).strip() for i in keywordList if str(i[5]) != 'nan']
            self.deposits = list(set(self.deposits))

            self.average_daily_balance = [str(i[8]).strip() for i in keywordList if str(i[8]) != 'nan']
            self.average_daily_balance = list(set(self.average_daily_balance))
            self.punctList = list(set(punctuation))

            self.directdep_keywords = [str(i[11]).strip() for i in keywordList if str(i[11]) != 'nan']
            self.directdep_keywords = list(set(self.directdep_keywords))
            print(self.directdep_keywords)

        except Exception as e:
            raise Exception(
                "Failed to extract values for payroll_keywords, cc_keywords, loan_keywords. Reason: " + str(e))

    def matches(self, large_string, query_string, threshold):
        for punct in self.punctList:
            large_string = large_string.replace(punct, " ")
        for punct in self.punctList:
            query_string = query_string.replace(punct, " ")
        n = len(query_string.split())

        grams = list(ngrams(large_string.split(), n))
        # grams = [i for i in grams if i.strip()!='']
        bestScores = 0
        strFound  = None
        for gram in grams:
            # bestScores
            gram = " ".join(gram)
            score = fuzz.partial_ratio(query_string, gram)
            if len(gram.split()) >= 2:
                ratios = [fuzz.partial_ratio(query_string, gram) > 90 for kth in gram.split()]
                if not re.search(r"\b" + query_string.lower() + r"\b", gram):
                    if False in ratios:
                        continue
            if fuzz.partial_ratio(query_string, gram) == 100:
                if not re.search(r"\b" + query_string.lower() + r"\b", gram.lower()):
                    continue
            if score>bestScores and score>=90:
                strFound  = gram
                bestScores  = score
        return strFound, large_string



    def __format_amount__(self, amount):
        try:
            amount = amount.replace(",","")

            amount = amount.replace("$", "")
            return float(amount.strip())
        except:
            return 0

    def __count__num__digits(self, s):
        return sum(c.isdigit() for c in s)

    def extract_summ_info(self, summ):
        employerName = []
        employeeName = []
        creditCardProvider = []
        directDepositAmounts =[]

        if 'payroll' in summ:
            for des, desVal in summ['payroll'].items():
                des = des.lower()
                for k in self.directdep_keywords:

                    k = k.lower()
                    wordsMatched, newdes = (self.matches(des, k, 0.9))
                    newdes
                    if wordsMatched != None:
                        directDepositAmounts.append(self.__format_amount__(str(desVal[1])))

                        desplited = newdes.split(k)
                        if len(desplited) >0:
                            employerName.append(desplited[0].strip())
                            desSplitted = des.split()
                            desSplitted = [i for i in desSplitted if i.strip() != '']
                            for desSp in desSplitted[::-1]:
                                lenInt = self.__count__num__digits(desSp)
                                if lenInt>5:
                                    allempnames= ' '.join(desSplitted[desSplitted.index(desSp)+1: -1])
                                    employeeName.extend(allempnames.split(","))
                        break
        if 'credit card' in summ:
            for des, desVal in summ['credit card'].items():
                des = des.lower()
                k = desVal[0]
                k = k.lower()
                wordsMatched,newdes = (self.matches(des, k, 0.9))
                if wordsMatched!=None:

                    if re.search(r"\b" + wordsMatched.lower() + r"\b", newdes.lower()):
                        desSplitted = newdes.split(wordsMatched)
                        if len(desSplitted)>0:
                            creditCardProvider.append(desSplitted[0].strip())

            # except:
            #     pass

        directDepositAmounts = sum(directDepositAmounts)
        return ", ".join(list(set(employerName))), ", ".join(list(set(employeeName))), ", ".join(list(set(creditCardProvider))),directDepositAmounts





# s1="BARCLAYCARD US   DES:CREDITCARD ID:XXXXXXXXX  INDN:KATHERINE WRIGHT        CO 85".lower()
# s2 = "credit card"
# print( list(matches(s1, s2, 0.9)))
if __name__ == "__main__":
    data = {'payroll': {'Ferguson Enterpr Dir Dep 190802 1908022001060 Thomas Crunk 2': ['Dir Dep ', 1346.72], 'Ferguson Enterpr Dir Dep 190802 1908021024816 Chelsea Crunk 3': ['Dir Dep ', 1512.13], 'Ferguson Enterpr Dir Dep 190816 1908161024816 Chelsea Crunk 6': ['Dir Dep ', 511.18], 'Ferguson Enterpr Dir Dep 190816 1908162001060 Thomas Crunk 7': ['Dir Dep ', 1295.43], 'Edeposit IN Branch/Store 08/22/19 12:27:20 Pm 850 Barrett Pkwy Kennesaw GA 9748 9': ['Edeposit IN', 200.0]}, 'credit card': {}, 'loan': {'Fedloanservicing Stdnt Loan 190816 6Nfliannae1 Chelsea E Knowles 80': ['Stdnt Loan', 291.28]}}


    obj = WFExtractSum()

    emp, empee, ccpro,directDepositAmounts = obj.extract_summ_info(data)
    print(emp)
    print(empee)
    print(ccpro)
    print(directDepositAmounts)