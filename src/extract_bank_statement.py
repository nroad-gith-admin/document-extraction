# from tika import parser
import sys, os, json
import xlwt

curpath = os.path.join(os.path.dirname(os.path.realpath(__file__)))
sys.path.insert(0, curpath)

from boa_bank_statement import BOABankExtraction
from jpmc_bank_statement import JPMCBankExtraction
from pnc_bank_statement import PNCBankExtraction
from us_bank_statement import USBankExtraction
from wf_bank_statement import WFBankExtraction

class BankExtraction:
    def __init__(self):
        self.boaObj = BOABankExtraction()
        self.jpmcObj = JPMCBankExtraction()
        self.pncObj = PNCBankExtraction()
        self.usObj = USBankExtraction()
        self.wfObj = WFBankExtraction()
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
        try:

            ##US bank: 0,1
            ## citi bank: 1
            if bankName.lower().strip() == "wells fargo":
                res = self.wfObj.extractBankStatement(pdfFile, pdfFileData, [1, 2, 2, ], docID)
            elif bankName.lower().strip() == "bank of america":
                res = self.boaObj.extractBankStatement(pdfFile, pdfFileData, [1, 2, 2, ], docID)


            elif bankName.lower().strip() == "jpmorgan chase bank":
                res = self.jpmcObj.extractBankStatement(pdfFile, pdfFileData, [1, 2, 2, ], docID)


            elif bankName.lower().strip() == "pnc bank":
                res = self.pncObj.extractBankStatement(pdfFile, pdfFileData, [1, 2, 2, ], docID)

            elif bankName.lower().strip() == "us bank":
                res = self.usObj.extractBankStatement(pdfFile, pdfFileData, [1, 2, 2, ], docID)



            else:
                res = {}



        except Exception as e:
            raise Exception("Failed to extract data. Reason: "+str(e))


        return res

if __name__=="__main__":
    pass

