from extract_bank_statement import BankExtraction


try:
    extractobj = BankExtraction()

except Exception as e:
    raise Exception("Failed to create BankExtraction object")

def extract(bankstatementLoc, pdfDataPath ,bankstatemntType, params, documentId):
    data = extractobj.extractBankStatement(bankstatementLoc, pdfDataPath, bankstatemntType, params, documentId)
    return data