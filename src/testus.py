import os
from extract_bank_statement import BankExtraction

import xlwt
workbook = xlwt.Workbook()
sheet = workbook.add_sheet('Top Banks Data')

headers = ["Sr.No",	"Unique ID",	"Documentation ID and Name",	"Name on the Account",	"Bank Name",	"Account Number",
           "Routing Number (if available)",	"Average Daily Balance (if available)",
           "Loan Deposits",	"Payroll Deposits",	"Direct Deposits",	"CC Payments",	"Loan Payments"]

extractobj = BankExtraction()
wellsfargofolder = r"/Users/prasingh/Prashant/Prashant/CareerBuilder/Extraction/data/BS_NT/BS_USTest"
files  = os.listdir(wellsfargofolder)
files = [os.path.join(wellsfargofolder,i)for i in files]
excelRow =0
for j, v1 in enumerate(headers):
    sheet.write(excelRow, j, v1)

for file in files:
    print(file)
    excelRow = excelRow+1   
    data = (extractobj.extractBankStatement(file, "us bank",[1,2,2,]))
    print(data)
    sheet.write(excelRow,0,excelRow)
    sheet.write(excelRow, 1, "")
    sheet   .write(excelRow, 2, file.split("/")[-1])
    sheet.write(excelRow, 3, data["nameOnTheAccount"])
    sheet.write(excelRow, 4, data["bankName"])
    sheet.write(excelRow, 5, data["accountNumber"])
    sheet.write(excelRow, 6, data["routingNumber"])
    sheet.write(excelRow, 7, data["averageDailyBalance"])
    sheet.write(excelRow, 8, data["loanDeposits"])
    sheet.write(excelRow, 9, data["payrollDeposits"])
    sheet.write(excelRow, 10, data["directDeposits"])
    sheet.write(excelRow, 11, data["CCPayments"])
    sheet.write(excelRow, 12, data["loanPayments"])
    # break

newfilename = "ExtractedDataUS_Results.xls"
workbook.save(newfilename)