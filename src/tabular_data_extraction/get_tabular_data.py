import sys, os

curpath = os.path.join(os.path.dirname(os.path.realpath(__file__)))
sys.path.insert(0, curpath)
from quantifyData import get_all_formatted
from table_extrator_camelot import TableExtractorCamelot
from PyPDF2 import PdfFileReader
from utils import *
import numpy as np
from statistics import mode
from collections import Counter

tableCamelotObj = TableExtractorCamelot()

def most_common(List):
    commons = []
    occurence_count = Counter(List)
    maxV = max(occurence_count.values())
    for k, v in occurence_count.items():
        if float(v/maxV)*100 > 80:
            commons.append(k)
    return commons
def get_tablular_data(filepath):
    tableData = []
    try:
        pdf = PdfFileReader(open(filepath, 'rb'))
    except Exception as e:
        raise Exception("Failed to read the file: " + str(filepath) + " Reason: " + str(e))
    num_pages = pdf.getNumPages()
    for page in range(1, num_pages + 1):
        try:
            tables = tableCamelotObj.extract_table(filepath, str(page))
        except:
            continue

        tables = list(set(tables))
        # if page == 3:
        #     print("we are 3rd")
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
        # print(tables)
        for table_i in range(len(tables)):
            data = tables[table_i].df
            data = data.applymap(clean_pandas)
            d = data.replace(r'^\s*$', np.nan, regex=True)
            d = d.isnull().all()
            ind = d.index[d].tolist()
            if len(ind) > 0:
                data = data.drop(ind, axis=1)

            data = data.values.tolist()
            data =  get_all_formatted(data)
            tableData.extend(data)
    lens = [len(i) for i in tableData]

    if len(lens)>0:
        mostCom = most_common(lens)
        tableData = [i for i in tableData if len(i)in mostCom ]

    return tableData


if __name__=="__main__":
    filepath = r"/Users/prasingh/Prashant/Prashant/CareerBuilder/Extraction/data/BS_NT/BS_US/0064O00000jteKqQAI-00P4O00001JkXBcUAN-__last_60_days_of_bank_stateme.pdf"
    filepath = r"/Users/prasingh/Prashant/Prashant/CareerBuilder/Extraction/data/BS_NT/BS_BOA/0064O00000k7RiOQAU-00P4O00001KTl0PUAT-__last_60_days_of_bank_stateme.pdf"
    # filepath = r"/Users/prasingh/Prashant/Prashant/CareerBuilder/Extraction/data/BS_NT/BS_Citi/0064O00000aDmSjQAK-00P4O00001JkSvIUAV-chetrum BS.pdf"
    # filepath = r"/Users/prasingh/Prashant/Prashant/CareerBuilder/Extraction/data/BS_NT/BS_Citi/0064O00000aDmSjQAK-00P4O00001JkSvIUAV-chetrum BS.pdf"
    # filepath = r"/Users/prasingh/Prashant/Prashant/CareerBuilder/pdftablereader/Bank_Statement_Parser/BankStatementParser/main/TableExtractor/bank_statements/PNCBANK_back/t/10915568605217091500/4-28-2017 Operating Statement.pdf"
    # filepath = r"/Users/prasingh/Prashant/Prashant/CareerBuilder/pdftablereader/Bank_Statement_Parser/BankStatementParser/main/TableExtractor/bank_statements/PNCBANK_back/t/20988146275217061400/April Bank.pdf"
    # tableCamelotObj = TableExtractorCamelot()
    # page = 4
    # tables = tableCamelotObj.extract_table(filepath, str(page))
    # for table_i in range(len(tables)):
    #     data = (tables[table_i].df).values.tolist()
    #     # for i, d in enumerate(data):
    #     #     print(i,list(d))
    #     for d in (get_all_formatted(data)):
    #         print(d)
    d = get_tablular_data(filepath)
    for  i in d:
        print(i)