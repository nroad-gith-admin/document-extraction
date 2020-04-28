import re, os
import pandas as pd
from fuzzywuzzy import fuzz, process
from string import punctuation
from nltk import ngrams



class JPMCExtractSum:
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

            self.directdep_keywords = [str(i[11]).strip() for i in keywordList if str(i[11]) != 'nan']
            self.directdep_keywords = list(set(self.directdep_keywords))

            self.punctList = list(set(punctuation))
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
                    if re.search(r"\b" + k.lower() + r"\b", des.lower()):
                        desplited = des.split(k)
                        if len(desplited) >0:
                            employerName.append(desplited[0].strip())
                            directDepositAmounts.append(self.__format_amount__(str(desVal[1])))
                            desplited = [j for i in desplited for j in i.split() if "INDN:".lower() in j]
                            if len(desplited)>0:
                                employeeName.extend(desplited[0].replace("INDN:".lower(),"").strip().split(","))
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
                            # break

        directDepositAmounts = sum(directDepositAmounts)
        return ", ".join(list(set(employerName))), ", ".join(list(set(employeeName))), ", ".join(list(set(creditCardProvider))),directDepositAmounts





# s1="BARCLAYCARD US   DES:CREDITCARD ID:XXXXXXXXX  INDN:KATHERINE WRIGHT        CO 85".lower()
# s2 = "credit card"
# print( list(matches(s1, s2, 0.9)))
if __name__ == "__main__":
    data = {
    'payroll': {
      '46837 Clearwater Dir Dep                    PPD ID: 1364227403 5': [
        'Dir Dep',
        4153.9
      ]
    },
    'credit card': {
      'Synchrony Bank   Cc Pymt    601918302263256 Web ID: 9856794001 29': [
        'CC PYMT',
        -70.0
      ],
      'Synchrony Bank   Cc Pymt    601918302263256 Web ID: 9856794001 115': [
        'CC PYMT',
        -60.0
      ],
      'Capital One      Crcardpmt  922930180080617 Tel ID: 9541719018 179': [
        'Crcardpmt',
        -25.0
      ]
    },
    'loan': {

    }
  }
    obj = JPMCExtractSum()

    emp, empee, ccpro,directDepositAmounts = obj.extract_summ_info(data)
    print(emp)
    print(empee)
    print(ccpro)
    print(directDepositAmounts)