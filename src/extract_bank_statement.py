# from tika import parser
import sys, os, json
import xlwt

curpath = os.path.join(os.path.dirname(os.path.realpath(__file__)))
sys.path.insert(0, curpath)

from image_data_extraction.get_data_image import ExtractDataImage
from tabular_info_extraction.boa_extraction_summary import BOAExtractSum
from tabular_info_extraction.boa_table_info import TableBOAInfoExtraction
from image_based_info_extraction.info_extraction import TableInfoExtractionImage
from staticCode.wellsfargo_static import ExtractWellsFargo
from staticCode.boa_static import ExtractBOA
from staticCode.jpmorganchase_static import ExtractJPMC
from staticCode.pnc_static import ExtractPNC
from staticCode.us_static import ExtractUS
from tabular_data_extraction.format1.extract_table_info2 import TableInfoExtraction2
from tabular_data_extraction.format2.extract_table_info3 import TableInfoExtraction3
from qa_checks.checks import check_all
# dataExtObj = DataExtractor()
extractDataImgObj = ExtractDataImage()
dataExtObj = ExtractWellsFargo()
dataExtObjBoa = ExtractBOA()
dataExtObjJpmc = ExtractJPMC()
dataExtObjPNC = ExtractPNC()
dataExtObjUS = ExtractUS()
tableInfoExtImg = TableInfoExtractionImage()
tableInfoObjBOA = TableBOAInfoExtraction()
tableInfoObj2 = TableInfoExtraction2()
tableInfoObj3 = TableInfoExtraction3()
boaSummaryExtraction = BOAExtractSum()


class BankExtraction:

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

    def extractBankStatement(self, pdfFile, pdfFileData, bankName, params, docID):
        payroll_amounts, cc_amounts, loan_amounts, deposits, averageBalance, summdata = "", "", "", "", "", None
        descriptionCol, depositCol, withdrawCol = params[0],params[1],params[2]
        BankData = {}
        try:

            ##US bank: 0,1
            ## citi bank: 1
            if bankName.lower().strip() == "wells fargo":
                if pdfFileData!=None and os.path.isdir(pdfFileData):
                    if  os.path.isdir(pdfFileData):
                        statementData = []
                        for jsonfile_i, jsonfile in enumerate(os.listdir(pdfFileData)):
                            if jsonfile_i in [0,1,]:
                            # if jsonfile == "0.pdf" or jsonfile == "1.pdf"
                                with open(os.path.join(pdfFileData, jsonfile)) as f:
                                    statementData.extend(json.load(f))
                else:
                    statementData = extractDataImgObj.get_data(pdfFile, [0, 1])
                data = dataExtObj.get_classified(statementData)
                _, _, _, deposits, averageBalance, _ = tableInfoObj.getTableInfo(
                    pdfFile, descriptionCol, depositCol, withdrawCol)
                additionKeywords, deductionKeywords = ["Transaction history", "Transaction history (continued)"], []
                headers1 = ["Date", "number", "description", "additions", "subtractions", "balance"]
                headers2 = ["Date", "number", "description", "credits", "debits", "balance"]
                allheaders = []
                allheaders.append(headers1)
                allheaders.append(headers2)

                payroll_amounts, cc_amounts, loan_amounts, summdata = tableInfoObj3.getTableInfo(pdfFile, None,
                                                                                                dateCol=0, desCol=2,
                                                                                                depositCol=-3,
                                                                                                withdrawCol=-2,
                                                                                                totalAmountsCol=3,
                                                                                                isKeywordsPage=True,
                                                                                                headers=allheaders,
                                                                                                additionKeywords=additionKeywords,
                                                                                                deductionKeywords=deductionKeywords)
            elif bankName.lower().strip() == "bank of america":
                if pdfFileData != None and os.path.isdir(pdfFileData):
                    if  os.path.isdir(pdfFileData):
                        statementData = []
                        for jsonfile_i, jsonfile in enumerate(os.listdir(pdfFileData)):
                            if jsonfile_i in [0,1,2,]:
                                with open(os.path.join(pdfFileData, jsonfile)) as f:
                                    statementData.extend(json.load(f))
                else:
                    statementData = extractDataImgObj.get_data(pdfFile, [0, 1, 2])

                data = dataExtObjBoa.get_classified(statementData)

                payroll_amounts, cc_amounts, loan_amounts,summdata = tableInfoObj2.getTableInfo(
                    pdfFile, 1, 2, 2)
                employerNames, employeeName, ccProviders = boaSummaryExtraction.extract_summ_info(summdata)
                _, _, _, deposits, averageBalance,begBalance, endBalance, withdrawAmounts, endDate, accounttype, _ = tableInfoObjBOA.getTableInfo(
                    pdfFile, descriptionCol, depositCol, withdrawCol)

            elif bankName.lower().strip() == "jpmorgan chase bank":
                if pdfFileData != None and os.path.isdir(pdfFileData):
                    if  os.path.isdir(pdfFileData):
                        statementData = []
                        for jsonfile_i, jsonfile in enumerate(os.listdir(pdfFileData)):
                            if jsonfile_i in [0,1,2,]:
                            # if jsonfile == "0.pdf" or jsonfile == "1.pdf"
                                with open(os.path.join(pdfFileData, jsonfile)) as f:
                                    statementData.extend(json.load(f))
                else:
                    statementData = extractDataImgObj.get_data(pdfFile, [0, 1, 2])

                data = dataExtObjJpmc.get_classified(statementData)

                payroll_amounts, cc_amounts, loan_amounts, deposits, averageBalance, summdata = tableInfoObj.getTableInfo(
                    pdfFile, descriptionCol, depositCol, withdrawCol)
                if payroll_amounts == 0 and cc_amounts==0 and loan_amounts==0 :
                    payroll_amounts, cc_amounts, loan_amounts, summdata = tableInfoObj2.getTableInfo(
                        pdfFile, 1, 2, 2)

            elif bankName.lower().strip() == "pnc bank":
                if pdfFileData != None and os.path.isdir(pdfFileData):
                    if  os.path.isdir(pdfFileData):
                        statementData = []
                        # for jsonfiles in os.listdir(pdfFileData):
                        for jsonfile_i, jsonfile in enumerate(os.listdir(pdfFileData)):
                            if jsonfile_i in [1,]:
                            # if jsonfile == "0.pdf" or jsonfile == "1.pdf"
                                with open(os.path.join(pdfFileData, jsonfile)) as f:
                                    statementData.extend(json.load(f))
                else:
                    statementData = extractDataImgObj.get_data(pdfFile, [1,])

                data = dataExtObjPNC.get_classified(statementData)

                payroll_amounts, cc_amounts, loan_amounts, summdata = tableInfoObj2.getTableInfo(
                    pdfFile, 1, 2, 2)

                _, _, _, deposits, averageBalance, _ = tableInfoObj.getTableInfo(
                    pdfFile, descriptionCol, depositCol, withdrawCol)

                if pdfFileData!=None:
                    if  os.path.isdir(pdfFileData):
                        statementData = []
                        for jsonfile_i, jsonfile in enumerate(os.listdir(pdfFileData)):
                            if jsonfile_i in [0,1,]:
                                with open(os.path.join(pdfFileData, jsonfile)) as f:
                                    statementData.extend(json.load(f))
                else:
                    statementData = extractDataImgObj.get_data(pdfFile, [0,1,])

                deposits, averageBalance = tableInfoExtImg.getTableInfo(statementData)

            elif bankName.lower().strip() == "us bank":
                if pdfFileData!=None:
                    if  os.path.isdir(pdfFileData):
                        statementData = []
                        for jsonfiles in os.listdir(pdfFileData):
                            for jsonfile_i, jsonfile in enumerate(jsonfiles):
                                if jsonfile_i in [0,]:
                                # if jsonfile == "0.pdf" or jsonfile == "1.pdf"
                                    with open(os.path.join(pdfFileData, jsonfiles)) as f:
                                        statementData.extend(json.load(f))
                else:
                    statementData = extractDataImgObj.get_data(pdfFile, [0,])
                # print(statementData)
                data = dataExtObjUS.get_classified(statementData)
                payroll_amounts, cc_amounts, loan_amounts, summdata = tableInfoObj2.getTableInfo(
                    pdfFile, descriptionCol, depositCol, withdrawCol)
                _, _, _, deposits, _, _ = tableInfoObj.getTableInfo(
                    pdfFile, descriptionCol, depositCol, withdrawCol,edge_tol=500)


            else:
                data = {}

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

            BankData["averageDailyBalance"] = averageBalance
            BankData["loanDeposits"] = -9999.99
            BankData["payrollDeposits"] = (payroll_amounts)
            BankData["CCPayments"] = (cc_amounts)
            BankData["loanPayments"] = (loan_amounts)
            BankData["directDeposits"] = (deposits)
            BankData["SummaryInfo"] = (summdata)
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

            headers = ["Sr.No", "Unique ID", "Documentation ID and Name", "Name on the Account", "Bank Name",
                       "Account Number",
                       "Routing Number (if available)", "Average Daily Balance (if available)",
                       "Loan Deposits", "Payroll Deposits", "Direct Deposits", "CC Payments", "Loan Payments"]

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
            sheet.write(excelRow, 10, BankData["directDeposits"])
            sheet.write(excelRow, 11, BankData["CCPayments"])
            sheet.write(excelRow, 12, BankData["loanPayments"])
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
    pdfFile = r"/Users/prasingh/Prashant/Prashant/CareerBuilder/Extraction/data/BS_NT/BS_BOA/0064O00000kIl2CQAS-00P4O00001KUc6QUAT-dwayne_foster_last_60_days_of_.pdf"
    pdfFileData = "/Users/prasingh/Prashant/Prashant/CareerBuilder/ExtractionCode/src/classifier/data/0064O00000kIl2CQAS-00P4O00001KUc6QUAT-dwayne_foster_last_60_days_of_"
    # # pdfFile = r"/Users/prasingh/Prashant/Prashant/CareerBuilder/Extraction/data/bankstatements/0064O00000jsjGtQAI-00P4O00001Ibc7AUAR-__last_60_days_of_bank_stateme.pdf"
    obj = BankExtraction()
    print(obj.extractBankStatement(pdfFile, pdfFileData,"bank of america",[1,2,2,],"boa1"))

    # pdffiles = r"/Users/prasingh/Prashant/Prashant/CareerBuilder/Extraction/data/testingpdf"
    # # print(os.listdir(pdffiles))
    # pdfData = (r"/Users/prasingh/Prashant/Prashant/CareerBuilder/Extraction/src/classifier/data")
    # for file in os.listdir(pdffiles):
    #     if ".DS_Store" not in file:
    #         pdfDataPath = os.path.join(pdfData,file.replace(".pdf",""))
    #
    #         file = os.path.join(pdffiles, file)
    #
    #         # print(file,pdfDataPath)
    #         obj = BankExtraction()
    #         if "wellsfargo" in file:
    #             d = obj.extractBankStatement(file,pdfDataPath,"wells fargo",[2,3,4],pdfDataPath.split("/")[-1])
    #             print(d)
    #         if "boa" in file:
    #             d=obj.extractBankStatement(file,pdfDataPath,"bank of america",[1,2,2,],pdfDataPath.split("/")[-1])
    #             print(d)
    #
    #         if "chase" in file:
    #             d= obj.extractBankStatement(file,pdfDataPath,"jpmorgan chase bank",[1,2,2,],pdfDataPath.split("/")[-1])
    #             print(d)
    #
    #         if "pnc" in file:
    #             d= obj.extractBankStatement(file,pdfDataPath,"pnc bank",[2,1,1,],pdfDataPath.split("/")[-1])
    #             print(d)

