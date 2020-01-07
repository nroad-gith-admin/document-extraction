# from tika import parser
import sys, os

curpath = os.path.join(os.path.dirname(os.path.realpath(__file__)))
sys.path.insert(0, curpath)

from image_data_extraction.get_data_image import ExtractDataImage
from extract_table_info import TableInfoExtraction
from image_based_info_extraction.info_extraction import TableInfoExtractionImage
# from model_based.data_extraction import DataExtractor
from staticCode.wellsfargo_static import ExtractWellsFargo
from staticCode.boa_static import ExtractBOA
from staticCode.jpmorganchase_static import ExtractJPMC
from staticCode.pnc_static import ExtractPNC
from staticCode.us_static import ExtractUS
from tabular_data_extraction.extract_table_info2 import TableInfoExtraction2
from qa_checks.checks import check_all
# dataExtObj = DataExtractor()
extractDataImgObj = ExtractDataImage()
dataExtObj = ExtractWellsFargo()
dataExtObjBoa = ExtractBOA()
dataExtObjJpmc = ExtractJPMC()
dataExtObjPNC = ExtractPNC()
dataExtObjUS = ExtractUS()
tableInfoExtImg = TableInfoExtractionImage()
tableInfoObj = TableInfoExtraction()
tableInfoObj2 = TableInfoExtraction2()


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

    def extractBankStatement(self, pdfFile,  bankName, params):
        payroll_amounts, cc_amounts, loan_amounts, deposits, averageBalance, summdata = "", "", "", "", "", None
        descriptionCol, depositCol, withdrawCol = params[0],params[1],params[2]
        BankData = {}
        try:

            ##US bank: 0,1
            ## citi bank: 1
            if bankName.lower().strip() == "wells fargo":
                statementData = extractDataImgObj.get_data(pdfFile, [0, 1])

                data = dataExtObj.get_classified(statementData)
                payroll_amounts, cc_amounts, loan_amounts, deposits, averageBalance, summdata = tableInfoObj.getTableInfo(
                    pdfFile, descriptionCol, depositCol, withdrawCol)

            elif bankName.lower().strip() == "bank of america":
                statementData = extractDataImgObj.get_data(pdfFile, [0, 1, 2])

                data = dataExtObjBoa.get_classified(statementData)
                payroll_amounts, cc_amounts, loan_amounts, deposits, averageBalance, summdata = tableInfoObj.getTableInfo(
                    pdfFile, descriptionCol, depositCol, withdrawCol)

            elif bankName.lower().strip() == "jpmorgan chase bank":
                statementData = extractDataImgObj.get_data(pdfFile, [0, 1, 2])

                data = dataExtObjJpmc.get_classified(statementData)
                payroll_amounts, cc_amounts, loan_amounts, deposits, averageBalance, summdata = tableInfoObj.getTableInfo(
                    pdfFile, descriptionCol, depositCol, withdrawCol)

            elif bankName.lower().strip() == "pnc bank":
                statementData = extractDataImgObj.get_data(pdfFile, [1,])

                data = dataExtObjPNC.get_classified(statementData)
                payroll_amounts, cc_amounts, loan_amounts, deposits, averageBalance, summdata = tableInfoObj.getTableInfo(
                    pdfFile, descriptionCol, depositCol, withdrawCol)
                statementData = extractDataImgObj.get_data(pdfFile, [0,])

                deposits = tableInfoExtImg.getTableInfo(statementData)

            elif bankName.lower().strip() == "us bank":
                statementData = extractDataImgObj.get_data(pdfFile, [0,])
                # print(statementData)
                data = dataExtObjUS.get_classified(statementData)
                payroll_amounts, cc_amounts, loan_amounts, deposits, averageBalance, summdata = tableInfoObj2.getTableInfo(
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

            BankData["averageDailyBalance"] = averageBalance
            BankData["loanDeposits"] = -9999.99
            BankData["payrollDeposits"] = (payroll_amounts)
            BankData["CCPayments"] = (cc_amounts)
            BankData["loanPayments"] = (loan_amounts)
            BankData["directDeposits"] = (deposits)
            BankData["SummaryInfo"] = (summdata)
            BankData["uniqueId"] = self.extractUniqueID(pdfFile)


            BankData = check_all(BankData)



        except Exception as e:
            raise Exception("Failed to covert into standard format. Reason: "+str(e))

        return BankData

if __name__=="__main__":
    pdfFile = r"/Users/prasingh/Prashant/Prashant/CareerBuilder/Extraction/data/BankStatementPDF/0060B00000ihIGEQA2-00P4O00001KoCcaUAF-Stacy Owens Oct BS.pdf"
    # pdfFile = r"/Users/prasingh/Prashant/Prashant/CareerBuilder/Extraction/data/BankStatementPDF/0064O00000jc6nkQAA-00P4O00001Jjzq1UAB-joseph_allen_last_60_days_of_b.pdf"
    # pdfFile = r"/Users/prasingh/Prashant/Prashant/CareerBuilder/Extraction/data/BankStatementPDF/0064O00000jc6nkQAA-00P4O00001Jjzq1UAB-joseph_allen_last_60_days_of_b.pdf"
    ## good case
    pdfFile = r"/Users/prasingh/Prashant/Prashant/CareerBuilder/Extraction/data/BankStatementPDF/0064O00000k8GTbQAM-00P4O00001Jlf4QUAR-latesha__cook_last_60_days_of_.pdf"
    obj = BankExtraction()
    # print(obj.extractBankStatement(pdfFile, 1, 2, 2))
    ##bad case
    pdfFile = r"/Users/prasingh/Prashant/Prashant/CareerBuilder/Extraction/data/BS_NT/BS_USTest/0064O00000kA0kAQAS-00P4O00001KCq10UAD-__last_60_days_of_bank_stateme.pdf"
    # pdfFile = r"/Users/prasingh/Prashant/Prashant/CareerBuilder/Extraction/data/bankstatements/0064O00000jsjGtQAI-00P4O00001Ibc7AUAR-__last_60_days_of_bank_stateme.pdf"
    # obj = BankExtraction()
    print(obj.extractBankStatement(pdfFile,"us bank",[1,2,2,]))