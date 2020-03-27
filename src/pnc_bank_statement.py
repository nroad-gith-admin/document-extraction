import sys, os, json
import xlwt

curpath = os.path.join(os.path.dirname(os.path.realpath(__file__)))
sys.path.insert(0, curpath)

from image_data_extraction.get_data_image import ExtractDataImage
from tabular_info_extraction.boa_extraction_summary import BOAExtractSum
from tabular_info_extraction.boa_table_info import TableBOAInfoExtraction
from staticCode.pnc_static import ExtractPNC
from tabular_data_extraction.format1.extract_table_info2 import TableInfoExtraction2
from qa_checks.checks import check_all
from image_based_info_extraction.info_extraction import TableInfoExtractionImage
from tabular_info_extraction.pnc_table_info import TablePNCInfoExtraction
from tabular_info_extraction.pnc_extraction_summary import PNCExtractSum

from negative_days.negative_days import negative_days_count

class PNCBankExtraction:

    def __init__(self):
        self.extractDataImgObj = ExtractDataImage()
        self.dataExtObjPNC = ExtractPNC()
        self.tableInfoObjBOA = TableBOAInfoExtraction()
        self.tableInfoObj2 = TableInfoExtraction2()
        self.boaSummaryExtraction = BOAExtractSum()
        self.tableInfoExtImg = TablePNCInfoExtraction()
        self.pncSummaryExtraction = PNCExtractSum()

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

    def extractBankStatement(self, pdfFile, pdfFileData, params, docID):
        payroll_amounts, cc_amounts, loan_amounts, deposits, averageBalance, summdata = "", "", "", "", "", None
        descriptionCol, depositCol, withdrawCol = params[0],params[1],params[2]
        lenData = 0
        BankData = {}
        try:

            if pdfFileData != None and os.path.isdir(pdfFileData):
                if os.path.isdir(pdfFileData):
                    statementData = []
                    # for jsonfiles in os.listdir(pdfFileData):
                    for jsonfile_i, jsonfile in enumerate(os.listdir(pdfFileData)):
                        if jsonfile_i in [1, ]:
                            # if jsonfile == "0.pdf" or jsonfile == "1.pdf"
                            with open(os.path.join(pdfFileData, jsonfile)) as f:
                                statementData.extend(json.load(f))
            else:
                statementData = self.extractDataImgObj.get_data(pdfFile, [1, ])

            data = self.dataExtObjPNC.get_classified(statementData)

            payroll_amounts, cc_amounts, loan_amounts, lenData, additionData, deductionData, summdata = self.tableInfoObj2.getTableInfo(
                pdfFile, 1, 2, 2)
            print(summdata)
            if pdfFileData != None:
                if os.path.isdir(pdfFileData):
                    statementData = []
                    for jsonfile_i, jsonfile in enumerate(os.listdir(pdfFileData)):
                        if jsonfile_i in [0, 1, ]:
                            with open(os.path.join(pdfFileData, jsonfile)) as f:
                                statementData.extend(json.load(f))
            else:
                statementData = extractDataImgObj.get_data(pdfFile, [0, 1, ])
            deposits, aveageBalance, begBalance, endBalance, withdrawAmounts, endDate, accounttype = self.tableInfoExtImg.getTableInfo(statementData)

            employerNames, employeeName, ccProviders, directDepositAmounts = self.pncSummaryExtraction.extract_summ_info(summdata)
            negativeDayeCount = negative_days_count(additionData, deductionData, begBalance)

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
            BankData["NegativeDaysCount"] = (negativeDayeCount)
            BankData["atLeastTenTransactions"] =lenData>10
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

            # headers = ["Sr.No", "Unique ID", "Documentation ID and Name", "Name on the Account", "Bank Name",
            #            "Account Number",
            #            "Routing Number (if available)", "Average Daily Balance (if available)",
            #            "Loan Deposits", "Payroll Deposits", "Direct Deposits", "CC Payments", "Loan Payments"]
            headers = ["Opp. ID", "Batch ID", "File ID / Name", "Name on the Account", "Bank Name", "Account Number",
             "Routing Number (if available)", "Average Daily Balance (if available)", "Loan Deposits",
             "Payroll Deposits", "Direct Deposits", "CC Payments", "Loan Payments",
             "Account Type", "Member Account Number(may be present)", "Current Balance", "Withdrawls / Debits",
             "As of Date", "Average Balance", "Negative Days", "Competitor Name", "Direct Deposit employer name",
             "Direct Deposit employee name", "Payroll Deposit employer name", "Credit Card Provider Name",
             "ACH Debits(Yes or No)", "At least 10 transactions"]

            excelRow = 0
            for j, v1 in enumerate(headers):
                sheet.write(excelRow, j, v1)
            excelRow = excelRow+1
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
            sheet.write(excelRow, 15,  BankData["endBalance"])
            sheet.write(excelRow, 16,  BankData["totalWithdraw"])
            sheet.write(excelRow, 17,  BankData["ToDate"])
            sheet.write(excelRow, 18,  BankData["averageDailyBalance"])
            sheet.write(excelRow, 19, BankData["NegativeDaysCount"])
            sheet.write(excelRow, 20,  '')
            sheet.write(excelRow, 21,  BankData["EmployersName"])
            sheet.write(excelRow, 22,  BankData["EmployeeNames"])
            sheet.write(excelRow, 23,  BankData["EmployersName"])
            sheet.write(excelRow, 24,  BankData["CCProviders"])
            sheet.write(excelRow, 25,  '')
            sheet.write(excelRow, 26,  lenData>10)

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
    # pdfFile = r"/Users/prasingh/Prashant/Prashant/CareerBuilder/Extraction/data/BS_NT/BS_BOA/0064O00000kIl2CQAS-00P4O00001KUc6QUAT-dwayne_foster_last_60_days_of_.pdf"
    # pdfFileData = "/Users/prasingh/Prashant/Prashant/CareerBuilder/ExtractionCode/src/classifier/data/0064O00000kIl2CQAS-00P4O00001KUc6QUAT-dwayne_foster_last_60_days_of_"
    # # # pdfFile = r"/Users/prasingh/Prashant/Prashant/CareerBuilder/Extraction/data/bankstatements/0064O00000jsjGtQAI-00P4O00001Ibc7AUAR-__last_60_days_of_bank_stateme.pdf"
    # obj = BankExtraction()
    # print(obj.extractBankStatement(pdfFile, pdfFileData,[1,2,2,],"boa1"))
    #
    #
    pdffiles = r"/Users/prasingh/Prashant/Prashant/CareerBuilder/Extraction/data/BS_NT/BS_PNC/"
    # print(os.listdir(pdffiles))
    pdfData = (r"/Users/prasingh/Prashant/Prashant/CareerBuilder/ExtractionCode/src/classifier/data/")
    toCSV = []
    for file in os.listdir(pdffiles):
        if ".DS_Store" not in file:
            pdfDataPath = os.path.join(pdfData,file.replace(".pdf",""))
            print(file)
            file = os.path.join(pdffiles, file)


            obj = PNCBankExtraction()


            d=obj.extractBankStatement(file,pdfDataPath,[1,2,2,],pdfDataPath.split("/")[-1])
            print(d)
            print('------------------------------------')
            toCSV.append(d)

    import csv

    keys = toCSV[0].keys()
    with open('pnc-res.csv', 'w') as output_file:
        dict_writer = csv.DictWriter(output_file, keys)
        dict_writer.writeheader()
        dict_writer.writerows(toCSV)




