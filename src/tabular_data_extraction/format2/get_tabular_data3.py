import sys, os

curpath = os.path.join(os.path.dirname(os.path.realpath(__file__)))
sys.path.insert(0, curpath)
from quantifyData3 import get_all_formatted
from table_extrator_camelot3 import TableExtractorCamelot
from PyPDF2 import PdfFileReader
from utils3 import *
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

def get_tablular_data(filepath, totalCol, dateCol, desCol, depositCol, withdrawCol, totalAmountsCol, isKeywordsPage, headers, additionKeywords,deductionKeywords):
    additionTable = []
    deductionTable = []
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
            # data, dateCol, desCol, depositCol, withdrawCol, totalAmountsCol = 1, isHeaderNewPage = True, headers = None
            additionData, deductionData =  get_all_formatted(data,dateCol, desCol, depositCol, withdrawCol, totalAmountsCol, isKeywordsPage, headers,additionKeywords,deductionKeywords)
            if len(additionData)>0:
                additionTable.extend(additionData)
            if len(deductionData)>0:
                deductionTable.extend(deductionData)
    lens = [len(i) for i in additionTable]

    if len(lens)>0:
        mostCom = most_common(lens)
        if totalCol!=None:
            additionTable = [i for i in additionTable if len(i)in mostCom or len(i)==totalCol]
        else:
            additionTable = [i for i in additionTable if len(i)in mostCom]

    lens = [len(i) for i in deductionTable]

    if len(lens) > 0:
        mostCom = most_common(lens)
        if totalCol!=None:
            dedctionTable = [i for i in deductionTable if len(i) in mostCom or len(i)==totalCol]
        else:
            dedctionTable = [i for i in deductionTable if len(i) in mostCom]

    return additionTable, deductionTable


if __name__=="__main__":
    filepath = r"/Users/prasingh/Prashant/Prashant/CareerBuilder/Extraction/data/BS_NT/BS_US/0064O00000jteKqQAI-00P4O00001JkXBcUAN-__last_60_days_of_bank_stateme.pdf"
    filepath = r"/Users/prasingh/Prashant/Prashant/CareerBuilder/Extraction/data/BS_NT/BS_Citi/0064O00000aDmSjQAK-00P4O00001JkSvIUAV-chetrum BS.pdf"
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
    # data, totalAmountsCol = 1, isHeaderNewPage = True, headers = None, depositCol = -3, withdrawCol = -2, desCol = 1
    # citi bank
    # additionKeywords, deductionKeywords = ["Checking activity", ], []
    # headers = ["Date", "description", "amount subtracted", "amount added", "balance"]
    # filepath = r"/Users/prasingh/Prashant/Prashant/CareerBuilder/Extraction/data/BS_NT/BS_Citi/0064O00000kIrdeQAC-00P4O00001KDGxyUAH-jonathan_veal_last_60_days_of_.pdf"
    # a, d = get_tablular_data(filepath, None, dateCol=0, desCol=1, depositCol=-2, withdrawCol=-3, totalAmountsCol=3,
    #                          isKeywordsPage=True, headers=headers, additionKeywords=additionKeywords,
    #                          deductionKeywords=deductionKeywords)
    # print(a)
    # print(d)
    ## wells fargo
    # import xlwt
    filepath = r"/Users/prasingh/Prashant/Prashant/CareerBuilder/Extraction/data/BS_NT/BS_JPMC"
    files = os.listdir(filepath)
    for file in files:

        ## wells fargo
        additionKeywords, deductionKeywords = ["Transaction history","Transaction history (continued)"],[]
        headers=["Date","number","description","additions","subtractions","balance"]
        print(os.path.join(filepath,file))
        # filepath = r"/Users/prasingh/Prashant/Prashant/CareerBuilder/Extraction/data/BS_NT/BS_WF/0064O00000k6B5kQAE-00P4O00001JkfySUAR-brett_costa_last_60_days_of_ba.pdf"
        a,d = get_tablular_data(os.path.join(filepath,file),None,dateCol=0, desCol=2, depositCol=-3, withdrawCol=-2, totalAmountsCol=3, isKeywordsPage=True, headers=headers, additionKeywords=additionKeywords, deductionKeywords=deductionKeywords)
        ## citi bank
        # print(file)
        # additionKeywords, deductionKeywords = ["Checking activity", ], []
        # try:
        #     headers = ["Date", "description", "amount subtracted", "amount added", "balance"]
        #     a, d = get_tablular_data(os.path.join(filepath,file), None, dateCol=0, desCol=1, depositCol=-2, withdrawCol=-3, totalAmountsCol=3,
        #                              isKeywordsPage=True, headers=headers, additionKeywords=additionKeywords,
        #                              deductionKeywords=deductionKeywords)
        #     print(a)
        #     print(d)
        ##jpmc
        # print(file)
        # additionKeywords, deductionKeywords = ["DEPOSITS AND ADDITIONS", ], ["ATM & DEBIT CARD WITHDRAWALS","ELECTRONIC WITHDRAWALS", "ELECTRONIC WITHDRAWALS (continued)","FEES"]
        # try:
        #     headers = ["Date", "description", "amount"]
        #     a, d = get_tablular_data(os.path.join(filepath,file), None, dateCol=0, desCol=1, depositCol=-2, withdrawCol=-2, totalAmountsCol=2,
        #                              isKeywordsPage=True, headers=headers, additionKeywords=additionKeywords,
        #                              deductionKeywords=deductionKeywords)
        #     print(a)
        #     print(d)
        #
        #
        #
        #
        #     workbook = xlwt.Workbook()
        #     sheet = workbook.add_sheet('deposits')
        #     sheet2 = workbook.add_sheet('withdrawls')
        #     for i,j in enumerate(a):
        #         sheet.write(i,0, j[0])
        #         sheet.write(i,1, j[1])
        #         sheet.write(i,2, j[2])
        #     for i,j in enumerate(d):
        #         sheet2.write(i,0, j[0])
        #         sheet2.write(i,1, j[1])
        #         sheet2.write(i,2, j[2])
        #
        #     newfilename = file.replace('pdf',"xls")
        #     workbook.save(newfilename)
        # except:
        #     pass
        # print("-----------------------------------")
        # break


    ### bank of america
    # additionKeywords, deductionKeywords = ["Deposits and other additions", ], ["Withdrawals and other subtractions","Withdrawals and other subtractions - continued","Other subtractions"]
    # headers = ["Date", "description", "amount"]
    # filepath = r"/Users/prasingh/Prashant/Prashant/CareerBuilder/Extraction/data/BS_NT/BS_BOA/0064O00000k7RiOQAU-00P4O00001KTl0PUAT-__last_60_days_of_bank_stateme.pdf"
    # a, d = get_tablular_data(filepath, None, dateCol=0, desCol=1, depositCol=-1, withdrawCol=-1, totalAmountsCol=1,
    #                          isKeywordsPage=True, headers=headers, additionKeywords=additionKeywords,
    #                          deductionKeywords=deductionKeywords)
    # print(a)
    # print(d)