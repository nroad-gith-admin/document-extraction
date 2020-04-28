import sys, os, json
import xlwt

curpath = os.path.join(os.path.dirname(os.path.realpath(__file__)))
sys.path.insert(0, curpath)

from image_data_extraction.get_data_image import ExtractDataImage
from tabular_info_extraction.jpmc_extraction_summary import JPMCExtractSum
from tabular_info_extraction.jpmc_table_info import TableJPMCInfoExtraction
from staticCode.jpmorganchase_static import ExtractJPMC
from tabular_data_extraction.format1.extract_table_info2 import TableInfoExtraction2
from tabular_data_extraction.format1.get_tabular_data import get_tablular_data
from qa_checks.checks import check_all
from tabular_info_extraction.extract_electronics import ExtractElectronics
from tabular_info_extraction.table_extrator_camelot import TableExtractorCamelot
from PyPDF2 import PdfFileReader
from tabular_info_extraction.utils import *
import numpy as np
from negative_days.negative_days import negative_days_count

from ach_debits.ach_debits import ACHDebits


class JPMCBankExtraction:

    def __init__(self):
        self.extractDataImgObj = ExtractDataImage()
        self.dataExtObjJPMC = ExtractJPMC()
        self.tableInfoObjJPMC = TableJPMCInfoExtraction()
        self.tableInfoObj2 = TableInfoExtraction2()
        self.jpmcSummaryExtraction = JPMCExtractSum()
        self.tableCamelotObj = TableExtractorCamelot()
        self.achDebitObj = ACHDebits()

    def isBankStatement(self,data):
        if not isinstance(data, str):
            raise Exception("Expecting data should in str. Got: " + type(data))

        if "bank of america" in data.lower():
            return True
        return False

    def extractUniqueID(self, pdfFileName):
        uniqueID = ""
        if ".pdf" not in pdfFileName:
            raise Exception("Expecting pdf file with extension .pdf")
        pdfFileName = pdfFileName.split("/")
        if len(pdfFileName)>0:
            pdfFileName = pdfFileName[-1]
            pdfFileName = pdfFileName.split("-")
            if len(pdfFileName)>0:
                uniqueID = pdfFileName[0]
        return uniqueID
    def __get_format_type__(self, pdfFile):
        header1 = "TRANSACTION DETAIL".lower()

        try:
            pdf = PdfFileReader(open(pdfFile, 'rb'))
        except Exception as e:
            raise Exception("Failed to read the file: "+str(filepath)+" Reason: "+str(e))
        num_pages = pdf.getNumPages()
        try:
            for page in range(1, num_pages + 1):
                try:
                    tables = self.tableCamelotObj.extract_table(pdfFile, str(page),edge_tol=500)
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
                        d1 = [i for i in d1 if i.strip()!='']
                        if len(d1) == 1 and str(d1[0]).lower().strip()==header1:
                            return 2
            return 1

        except Exception as e:
            print(e)
            pass
        return 1
    def separate_format2_jpmc(self, transData):
        additionData =[]
        deductionData = []
        for tranD in transData:
            if "-" in str(tranD[-2]):
                deductionData.append(tranD)
            else:
                additionData.append(tranD)
        return additionData, deductionData
    def extractBankStatement(self, pdfFile, pdfFileData, params, docID):
        payroll_amounts, cc_amounts, loan_amounts, deposits, averageBalance, summdata = "", "", "", "", "", None
        descriptionCol, depositCol, withdrawCol = params[0],params[1],params[2]
        lenData = 0
        BankData = {}
        try:
            if pdfFileData != None and os.path.isdir(pdfFileData):
                if os.path.isdir(pdfFileData):
                    statementData = []
                    for jsonfile_i, jsonfile in enumerate(os.listdir(pdfFileData)):
                        if jsonfile_i in [0, 1, 2, ]:
                            # if jsonfile == "0.pdf" or jsonfile == "1.pdf"
                            with open(os.path.join(pdfFileData, jsonfile)) as f:
                                statementData.extend(json.load(f))
            else:
                statementData = self.extractDataImgObj.get_data(pdfFile, [0, 1, 2])

            data = self.dataExtObjJPMC.get_classified(statementData)


            ## Get Transaction Format of the jpmc bank

            formatBank = self.__get_format_type__(pdfFile)
            if formatBank == 1:
                payroll_amounts, cc_amounts, loan_amounts, lenData, additionData, deductionData ,summdata = self.tableInfoObj2.getTableInfo(
                    pdfFile, 1, 2, 2)
            elif formatBank ==2:
                additionData, deductionData = get_tablular_data(pdfFile, 3)
                additionData, deductionData = self.separate_format2_jpmc(deductionData)
                # print(additionData)
                # print(deductionData)
                lenData = len(additionData)+len(deductionData)
                payroll_amounts, cc_amounts, loan_amounts, summdata = self.tableInfoObj2.getTableInfoData(additionData, deductionData, descriptionCol=1, depositCol = 2, withdrawCol=2)

            employerNames, employeeName, ccProviders, directDepositAmounts = self.jpmcSummaryExtraction.extract_summ_info(
                summdata)

            deposits, averageBalance, begBalance, endBalance, withdrawAmounts, endDate, accounttype = self.tableInfoObjJPMC.getTableInfo(
                pdfFile, descriptionCol, depositCol, withdrawCol)
            negativeDayeCount = negative_days_count(additionData, deductionData, begBalance)

            isAchDebit = self.achDebitObj.is_ach(additionData, deductionData, 1)

            new_s = {}
            for k, v in data.items():
                max_val = max(v.values())
                all_k = [i for i, j in v.items() if j == max_val]
                new_s[k] = ",".join(all_k)
            data =  new_s

        except Exception as e:
            raise Exception("Failed to extract data. Reason: "+str(e))

        try:
            try:
                BankData["nameOnTheAccount"] = data["ACNTHOLDNAME"]
            except:
                BankData["nameOnTheAccount"] = ""
            try:
                BankData["accountNumber"] = data["ACCOUNTNUM"]
            except:
                BankData["accountNumber"] = ""
            try:
                BankData["bankName"] = data["BANKNAME"]
            except:
                BankData["bankName"] = ""
            try:
                BankData["routingNumber"] = data["ROUTINGNUM"]
            except:
                BankData["routingNumber"] = ""
            if averageBalance ==0:
                averageBalance = -9999.99
            if payroll_amounts ==0:
                payroll_amounts = -9999.99
            if cc_amounts ==0:
                cc_amounts = -9999.99
            if loan_amounts ==0:
                loan_amounts = -9999.99
            if deposits ==0:
                deposits = -9999.99

            if lenData>10:
                atleast10trans = 'YES'
            else:
                atleast10trans = 'NO'


            BankData["begBalance"] = begBalance
            BankData["endBalance"] = endBalance
            BankData["ToDate"] = endDate
            BankData["totalWithdraw"] = withdrawAmounts
            BankData["accountType"] = accounttype
            BankData["EmployeeNames"] = employeeName
            BankData["EmployersName"] = employerNames
            BankData["CCProviders"] = ccProviders
            BankData["DirectDepositsAmounts"] = directDepositAmounts

            BankData["averageDailyBalance"] = averageBalance
            BankData["loanDeposits"] = -9999.99
            BankData["payrollDeposits"] = (payroll_amounts)
            BankData["CCPayments"] = (cc_amounts)
            BankData["loanPayments"] = (loan_amounts)
            BankData["directDeposits"] = (deposits)
            BankData["SummaryInfo"] = (summdata)
            BankData["atLeastTenTransactions"] =atleast10trans
            BankData["NegativeDaysCount"] = (negativeDayeCount)
            BankData["isACHDebit"] = isAchDebit

            # BankData["uniqueId"] = self.extractUniqueID(pdfFile)


            BankData = check_all(BankData)


            try:
                if not os.path.isdir("/data/"+str(docID)):
                    os.mkdir("/data/"+str(docID))
                path = os.path.join("/","data",str(docID),pdfFile.split("/")[-1].replace(".pdf",".xls"))
                fileWriten  = path
                fileToWrite = path
            except Exception as e:
                if not os.path.isdir(os.path.join(os.getcwd(),"output")):
                    os.mkdir("output")
                if not os.path.isdir(os.path.join(os.getcwd(),"output",str(docID))):
                    os.mkdir(os.path.join(os.getcwd(),"output",str(docID)))
                path = os.path.join(os.getcwd(),"output",str(docID), pdfFile.split("/")[-1].replace(".pdf",".xls"))
                fileWriten = path
                fileToWrite = path

            workbook = xlwt.Workbook()
            sheet = workbook.add_sheet('Top Banks Data')

            headers = ["Opp. ID", "Batch ID", "File ID / Name", "Name on the Account", "Bank Name", "Account Number",
                       "Routing Number (if available)", "Average Daily Balance (if available)", "Loan Deposits",
                       "Payroll Deposits", "Direct Deposits", "CC Payments", "Loan Payments",
                       "Account Type", "Member Account Number(may be present)", "Current Balance",
                       "Withdrawls / Debits",
                       "As of Date", "Average Balance", "Negative Days", "Competitor Name",
                       "Direct Deposit employer name",
                       "Direct Deposit employee name", "Payroll Deposit", "employer name", "Credit Card Provider Name",
                       "ACH Debits(Yes or No)", "At least 10 transactions"]

            excelRow = 0
            for j, v1 in enumerate(headers):
                sheet.write(excelRow, j, v1)
            excelRow = excelRow + 1
            sheet.write(excelRow, 0, excelRow)
            sheet.write(excelRow, 1, "")
            sheet.write(excelRow, 2, pdfFile.split("/")[-1])
            sheet.write(excelRow, 3, BankData["nameOnTheAccount"])
            sheet.write(excelRow, 4, BankData["bankName"])
            sheet.write(excelRow, 5, BankData["accountNumber"])
            sheet.write(excelRow, 6, BankData["routingNumber"])
            sheet.write(excelRow, 7, BankData["averageDailyBalance"])
            sheet.write(excelRow, 8, BankData["loanDeposits"])
            sheet.write(excelRow, 9, BankData["payrollDeposits"])
            sheet.write(excelRow, 10, BankData["DirectDepositsAmounts"])
            sheet.write(excelRow, 11, BankData["CCPayments"])
            sheet.write(excelRow, 12, BankData["loanPayments"])
            sheet.write(excelRow, 13, BankData["accountType"])
            sheet.write(excelRow, 14, '')
            sheet.write(excelRow, 15, BankData["endBalance"])
            sheet.write(excelRow, 16, BankData["totalWithdraw"])
            sheet.write(excelRow, 17, BankData["ToDate"])
            sheet.write(excelRow, 18, BankData["averageDailyBalance"])
            sheet.write(excelRow, 19, BankData["NegativeDaysCount"])
            sheet.write(excelRow, 20, '')
            sheet.write(excelRow, 21, BankData["EmployersName"])
            sheet.write(excelRow, 22, BankData["EmployeeNames"])
            sheet.write(excelRow, 23, BankData["EmployersName"])
            sheet.write(excelRow, 24, BankData["CCProviders"])
            sheet.write(excelRow, 25, BankData['isACHDebit'])
            sheet.write(excelRow, 26, BankData["atLeastTenTransactions"] )
            # sheet.write(excelRow, 13, str(data["SummaryInfo"]))
            workbook.save(fileToWrite)

            # fileWriten = os.path.join(os.getcwd(), fileToWrite)
            BankData["filepath"] = fileWriten
        except Exception as e:
            raise Exception("Failed to covert into standard format. Reason: "+str(e))

        return BankData

if __name__=="__main__":
    # pdfFile = r"/Users/prasingh/Prashant/Prashant/CareerBuilder/Extraction/data/BankStatementPDF/0060B00000ihIGEQA2-00P4O00001KoCcaUAF-Stacy Owens Oct BS.pdf"
    # # pdfFile = r"/Users/prasingh/Prashant/Prashant/CareerBuilder/Extraction/data/BankStatementPDF/0064O00000jc6nkQAA-00P4O00001Jjzq1UAB-joseph_allen_last_60_days_of_b.pdf"
    # # pdfFile = r"/Users/prasingh/Prashant/Prashant/CareerBuilder/Extraction/data/BankStatementPDF/0064O00000jc6nkQAA-00P4O00001Jjzq1UAB-joseph_allen_last_60_days_of_b.pdf"
    # ## good case
    # pdfFile = r"/Users/prasingh/Prashant/Prashant/CareerBuilder/Extraction/data/BankStatementPDF/0064O00000k8GTbQAM-00P4O00001Jlf4QUAR-latesha__cook_last_60_days_of_.pdf"
    # obj = BankExtraction()
    # # print(obj.extractBankStatement(pdfFile, 1, 2, 2))
    # ## bad case
    pdfFile = r"/Users/prasingh/Prashant/Prashant/CareerBuilder/Extraction/data/BS_NT/BS_JPMC_Test/0064O00000k90IxQAI-00P4O00001KSxdvUAD-Bank Statement.pdf"
    pdfFileData = "/Users/prasingh/Prashant/Prashant/CareerBuilder/ExtractionCode/src/classifier/data/0064O00000k90IxQAI-00P4O00001KSxdvUAD-Bank Statement"
    # # pdfFile = r"/Users/prasingh/Prashant/Prashant/CareerBuilder/Extraction/data/bankstatements/0064O00000jsjGtQAI-00P4O00001Ibc7AUAR-__last_60_days_of_bank_stateme.pdf"
    obj = JPMCBankExtraction()
    # print(obj.extractBankStatement(pdfFile, pdfFileData,[1,2,2,],"boa1"))
    #
    #


    pdffiles = r"/Users/prasingh/Prashant/Prashant/CareerBuilder/Extraction/data/BS_NT/BS_JPMC_Test"
    # print(os.listdir(pdffiles))
    pdfData = (r"/Users/prasingh/Prashant/Prashant/CareerBuilder/ExtractionCode/src/classifier/data/")
    toCSV = []
    for file in os.listdir(pdffiles):
        if ".DS_Store" not in file:
            print(file)
            pdfDataPath = os.path.join(pdfData,file.replace(".pdf",""))

            file = os.path.join(pdffiles, file)


            # obj = BankExtraction()


            d=obj.extractBankStatement(file,pdfDataPath,[1,2,2,],pdfDataPath.split("/")[-1])
            print(d)
            print('------------------------------------')
            toCSV.append(d)

    import csv

    keys = toCSV[0].keys()
    with open('jpmc-res.csv', 'w') as output_file:
        dict_writer = csv.DictWriter(output_file, keys)
        dict_writer.writeheader()
        dict_writer.writerows(toCSV)




