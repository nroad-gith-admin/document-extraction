import sys, os

curpath = os.path.join(os.path.dirname(os.path.realpath(__file__)))
sys.path.insert(0, curpath)

import pandas as pd
import re
import os
from fuzzywuzzy import fuzz


class ACHDebits:

    def __init__(self):
        keywordListFol = os.path.join(os.path.dirname(os.path.realpath(__file__)) ,"..","..","data", "Keywords_BS.XLSX")
        if os.path.isfile(keywordListFol) == False:
            raise Exception("Keyword List file not found in the directory: "+str(keywordListFol))


        try:
            keywordList = (pd.read_excel(keywordListFol)).values.tolist()
        except Exception as e:
            raise Exception("Failed to read the keyword list file. Reason: "+str(e))

        try:
            self.achKeywords = [str(i[13]).strip() for i in keywordList if str(i[13]) != 'nan']
            self.achKeywords = list(set(self.achKeywords))

            self.achKeywords2 = [str(i[14]).strip() for i in keywordList if str(i[14]) != 'nan']
            self.achKeywords.extend(list(set(self.achKeywords2)))
            print(self.achKeywords)
        except Exception as e:
            raise Exception("Failed to extract values for payroll_keywords, cc_keywords, loan_keywords. Reason: "+str(e))


    def is_ach(self, additionData, deductionData, descriptionCol):
        data = []
        data.extend(additionData)
        data.extend(deductionData)
        data = pd.DataFrame.from_records(additionData)
        for data_index, d in (data.iterrows()):
            d1 = d
            for k in self.achKeywords:
                if fuzz.partial_ratio(k.lower(), d1[descriptionCol].lower()) > 90:
                    if len(k.split()) >= 2:
                        ratios = [fuzz.partial_ratio(kth.lower(), d1[descriptionCol].lower()) > 90 for kth in
                                  k.split()]
                        if not re.search(r"\b" + k.lower() + r"\b", d1[descriptionCol].lower()):
                            if False in ratios:
                                continue
                    if fuzz.partial_ratio(k.lower(), d1[descriptionCol].lower()) == 100:
                        if not re.search(r"\b" + k.lower() + r"\b", d1[descriptionCol].lower()):
                            continue
                    return "YES"

        return "NO"



if __name__ == "__main__":
    obj = ACHDebits()

