from extract_bank_statement import BankExtraction


try:
    extractobj = BankExtraction()

except Exception as e:
    raise Exception("Failed to create BankExtraction object")

def extract(bankstatementLoc, bankstatemntType, params):
    data = extractobj.extractBankStatement(bankstatementLoc,bankstatemntType, params)
    return data