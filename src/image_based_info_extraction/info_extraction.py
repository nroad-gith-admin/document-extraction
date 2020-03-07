import xlrd
import pandas as pd
import numpy as np
import re
import os


class TableInfoExtractionImage:

    def __init__(self):

        keywordListFol = os.path.join(os.path.dirname(os.path.realpath(__file__)), ".." ,"..","data", "Keywords_BS.XLSX")
        if os.path.isfile(keywordListFol) == False:
            raise Exception("Keyword List file not found in the directory: "+str(keywordListFol))



        try:
            keywordList = (pd.read_excel(keywordListFol)).values.tolist()
        except Exception as e:
            raise Exception("Failed to read the keyword list file. Reason: "+str(e))

        try:

            self.deposits =[str(i[5]).strip() for i in keywordList if str(i[5]) !='nan']
            self.deposits = list(set(self.deposits))

            self.average_daily_balance = [str(i[8]).strip() for i in keywordList if str(i[8]) != 'nan']
            self.average_daily_balance = list(set(self.average_daily_balance))

            self.begBalanceKey = ["Beginning balance", ]
            self.endBalanceKey = ["Ending balance",]
            self.withdrawlKey = ["Checks and other deductions", ]
            self.accountTypeKey = ["Performance,Statement",]

            # print(self.average_daily_balance)
        except Exception as e:
            raise Exception("Failed to extract values for payroll_keywords, cc_keywords, loan_keywords. Reason: "+str(e))
    def checkMoney(self, val):
        val = val.replace("$","")

        val = val.replace(".", "")

        val = val.replace(",", "")
        val = val.strip()
        try:
            int(val)
            return True
        except:
            return False

    def __format_amount__(self, amount):
        try:
            amount = amount.replace(",","")

            amount = amount.replace("$", "")
            return float(amount.strip())
        except:
            return 0


    def getTableInfo(self, data):
        depositAmount = 0
        avgDailyBalance = 0
        try:
            for data_index, d in enumerate(data):
                d1 =re.sub(' +', ' ',d.replace("NEWLINE",""))
                # print(d1)
                try:

                    for k in self.deposits:
                        if  k.lower() in d1.lower():
                            d1 = d1.lower().partition(k.lower())
                            d1 = [i for i in d1 if i.strip()!='']
                            d1 = d1[d1.index(k.lower())+1]
                            d1 = d1.split()[0]

                            if self.checkMoney(d1) == True:
                                depositAmount = self.__format_amount__((d1))
                                break
                    for k in self.average_daily_balance:
                        if  k.lower() in d1.lower():
                            d1 = d1.lower().partition(k.lower())
                            d1 = [i for i in d1 if i.strip()!='']
                            d1 = d1[d1.index(k.lower())+1]
                            d1 = d1.split()[0]

                            if self.checkMoney(d1) == True:
                                avgDailyBalance = self.__format_amount__((d1))
                                break

                except IndexError as e:
                    pass
        except Exception as e:
            raise Exception("Something messed up. Reason: "+str(e))
        return  depositAmount, avgDailyBalance

if __name__=="__main__":
    tableInfoObj = TableInfoExtractionImage()
    # filepath  = r'/Users/prasingh/Prashant/Prashant/CareerBuilder/Extraction/data/BS_NT/BS_PNC/0064O00000kBOB5QAO-00P4O00001JkMbIUAV-shawn_frick_last_60_days_of_ba.pdf'
    data = ['Performance Checking Statement', '@© PNC BANK', 'Primary account number: 42-2543-9493 NEWLINE Page 1 of 7 NEWLINE Number of enclosures: 0', 'For the period', '08/10/2019 to 09/11/2019', 'gg For 24-hour banking, and transaction or NEWLINE interest rate information, sign-on to NEWLINE t PNC Bank Online Banking at pnc.com NEWLINE For customer service call 1-888-PNC-BANK NEWLINE Monday - Friday: 7 AM - 10 PM ET NEWLINE Saturday & Sunday: 8 AM - 5 PM ET NEWLINE Para servicio en espanol, 1-866-HOLA-PNC NEWLINE Moving? Please contact us at 1-888-PNC-BANK', 'SHAWN A FRICK NEWLINE 569 NORTHEAST AVE NEWLINE TALLMADGE OH 44278-1567', '® write to: Customer Service NEWLINE PO Box 609 NEWLINE Pittsburgh, PA 15230-9738 NEWLINE RB Visit us at pnc.com NEWLINE TDD terminal: 1-800-531-1648 NEWLINE For hearing impaired clients only NEWLINE IMPORTANT INFORMATION ABOUT CONSUMER CHECK PRICES AND QUANTITIES', 'Effective July 28, 2019, check order quantities for consumer check designs, excluding PNC Custom and NEWLINE Wallet/Wallet Duplicate D listed below’, will decrease from 100 to 80 checks.', 'Effective September 1, 2019, prices for PNC Custom and Wallet/Wallet Duplicate D check designs listed below* NEWLINE will increase.', '*PNC Custom and Wallet/Wallet Duplicate D check designs: Wallet PNC Exclusive, Wallet Duplicate PNC NEWLINE Exclusive, Wallet Pittsburgh Steelers, Wallet Pittsburgh Pirates, Wallet Washington Nationals, Wallet PNC NEWLINE Polish Check, Wallet Duplicate Wilkes-Barre Baby Penguins, Wallet Blue Safety, Wallet Green Safety, Wallet NEWLINE Yellow Safety, Wallet Blue Sheffield, Wallet Maroon Sheffield, Wallet Green Sheffield, Wallet Duplicate Blue NEWLINE Safety, Wallet Duplicate Green Safety, Wallet Duplicate Yellow Safety, Wallet Duplicate Blue Sheffield, NEWLINE Wallet Duplicate Maroon Sheffield and Wallet Duplicate Green Sheffield.', 'If you have questions regarding these changes, please call the number at the top of this statement or visit a NEWLINE PNC branch. NEWLINE IMPORTANT ACCOUNT INFORMATION FOR ALL CONSUMER CHECKING AND SAVINGS CUSTOMERS', 'The information below amends certain information in our Consumer Schedule of Service Charges and Fees NEWLINE (‘Schedule’) and our Virtual Wallet Features and Fees (‘Schedule’). All other information in our Schedule NEWLINE continues to apply to your account. Please read this information and retain it with your records.', 'Effective September 13, 2019, the $10 annual fee will no longer be assessed for a PNC Banking Card.', 'If you have any questions, please feel free to stop by a local PNC Branch or call the Customer Care Center at NEWLINE 1-888-762-2265. NEWLINE IMPORTANT ACCOUNT INFORMATION FOR ALL CONSUMER CHECKING CUSTOMERS', 'The information below amends certain information in our Consumer Schedule of Service Charges and Fees NEWLINE (‘Schedule’) and our Virtual Wallet Features and Fees (‘Schedule’). All other information in our Schedule NEWLINE continues to apply to your account. Please read this information and retain it with your records.', 'Performance Checking Statement', 'For the period 08/10/2019 to 09/11/2019 NEWLINE SHAWN A FRICK NEWLINE  NEWLINE Primary account number: 42-2543-9493 NEWLINE Page 2 of 7', '§& For 24-hour information,sign on to PNC Bank Online Banking NEWLINE on pne.com NEWLINE Account Number: 42-2543-9493 - continued', 'Effective September 13, 2019, the $10 annual fee will no longer be assessed for the following Affinity Visa NEWLINE Debit Cards: NEWLINE  NEWLINE Pittsburgh Pirates (PNC Park), Pittsburgh Steelers, WBS Penguins, Washington Nationals, Chicago Bears, NEWLINE Cincinnati Reds', "If you have any questions, please feel free to stop by a local PNC Branch or call the Customer Care Center at NEWLINE 1-888-762-2265. NEWLINE Watch Where You Click NEWLINE Be sure the emails, texts and phone calls you receive are from a trusted source and do not give out personal NEWLINE information, such as credit card numbers, Social Security numbers or other banking details, unless you have NEWLINE verified the sender. If you are unsure, contact PNC directly by typing www.pnc.com into your Internet browser NEWLINE or call PNC using a phone number provided on the www.pnc.com website. DO NOT use contact information NEWLINE contained in the suspect email or text. If you suspect you've received a fraudulent text message that appears NEWLINE to be from PNC, take a screen shot of the text message on your mobile phone and forward it to PNC Abuse NEWLINE (abuse@pnc.com). NEWLINE Performance Checking SHAWN AERICK NEWLINE Interest Checking Account Summary NEWLINE Account number: 42-2543-9493 NEWLINE Overdraft Protection has not been established for this account. NEWLINE Please contact us if you would like to set up this service. NEWLINE  NEWLINE Overdraft Coverage NEWLINE - Your account is currently NEWLINE Opted-Out. NEWLINE Balance Summary NEWLINE  NEWLINE Beginning Deposits and Checks and other Ending NEWLINE  NEWLINE balance other additions deductions balance NEWLINE 1,547.52 5,514.51 7,339.72 277.69-", 'Checks and other NEWLINE deductions NEWLINE 7,339.72 NEWLINE  NEWLINE Average monthly NEWLINE  NEWLINE balance NEWLINE 1,400.16', 'Ending NEWLINE balance NEWLINE 277.69- NEWLINE Charges NEWLINE and fees NEWLINE 68.75', 'Transaction Summary NEWLINE Checks Debit Card POS _Debit Card/Bankcard NEWLINE paid/withdrawals _ signed transactions POS PIN transactions NEWLINE 1 67 28 NEWLINE Total ATM PNC Bank ATM Other Bank ATM NEWLINE transactions transactions transactions NEWLINE 1 0 1', 'As of 09/11, a total of $.06 in interest NEWLINE was paid this year.', 'Interest Summary', 'Annual Percentage Number of days in NEWLINE Yield Earned (APYE) interest period', 'Average collected NEWLINE balance for APYE', 'Interest NEWLINE Earned this NEWLINE period NEWLINE  NEWLINE 01', '0.01%', '1,421.69', 'Overdraft and Returned Item Fee Summary NEWLINE Total for this Period', 'Total Year to Date', 'Total Overdraft Fees']


    depositAmount,avgDailyBalance= tableInfoObj.getTableInfo(data)
    print("deposit amount: ", depositAmount)
    print("avgDailyBalance amount: ", avgDailyBalance)

