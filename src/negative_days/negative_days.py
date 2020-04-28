from datetime import datetime

def format_amount( amount):
    amount  = str(amount)

    amount = amount.replace(",","")

    amount = amount.replace("$", "")
    amount = amount.replace("-","")

    return float(amount.strip())


def sortDate(allCols):
    '''
    date format:  08/09/19
    date_str = '09/19/2018'
    date_object = datetime.strptime(date_str, '%m/%d/%Y').date()

    '''
    try:
        allCols = [[datetime.strptime(i[0],'%m/%d/%y' ),i[-2],i[-1]] for i in allCols]
    except:

        try:
            allCols = [[datetime.strptime(i[0],'%m/%d' ),i[-2],i[-1]] for i in allCols]
        except:


            try:
                allCols = [[datetime.strptime(i[0],'%b %d' ),i[-2],i[-1]] for i in allCols]
            except Exception as e:
                print(e)
    return allCols


def negative_days_count(depositCol, withdrawCol, begBalance):
    count = 0
    allCols = []
    depositCol = [[i[0],format_amount(i[-1]), 1] for i  in depositCol]
    withdrawCol = [[i[0],format_amount(i[-1]) , -1] for i  in withdrawCol]
    allCols.extend(depositCol)
    allCols.extend(withdrawCol)
    data = sortDate(allCols)
    sortedD = sorted(data, key=lambda x: x[0])
    alldates = {}
    for i in sortedD:
        if i[-1] == 1:
            begBalance = begBalance+i[-2]

        else:
            begBalance = begBalance-i[-2]

        if begBalance < 0:
            alldates[i[0]] =1

    return len(alldates)




if __name__ =="__main__":
    ad =[['Aug 23', 'Electronic Deposit From TITAN LOGISTIC S', 1000.31], ['Aug 27', 'Visa Direct Cash App*Cash Ou 6208261821', 5.94], ['Aug 28', 'Visa Direct Cash App*Cash Ou 8208271915', 1.06], ['Aug 30', 'Electronic Deposit From TITAN LOGISTIC S', 463.97], ['Sep', '6 Electronic Deposit From TITAN LOGISTIC S', 833.31], ['Sep 11', 'Debit Purchase Ret - VISA On 091019 EUCLID OH 4091541000', 4.0], ['Sep 13', 'Electronic Deposit From TITAN LOGISTIC S', 857.82]]

    ded = [['Sep', '5 Fee ATM Withdrawal At Other Network 0500001168 $', -2.5], ['Aug 19', 'Debit Purchase - VISA On 081819 ORLANDO FL 1200688200 $', -12.66], ['Aug 19', 'Debit Purchase - VISA On 081719 GROUPON.COM  IL 9100661794', -106.0], ['Aug 19', 'Debit Purchase - VISA On 081719 GROUPON.COM  IL 9100661973', -124.0], ['Aug 30', 'Debit Purchase - VISA On 082819 CLEVELAND OH 1180800219', -3.0], ['Aug 30', 'Debit Purchase WALGREENS STORE  CLEVELAND   OH 0008301614', -12.37], ['Sep', '4 Debit Purchase ALDI 63047 NORTH RANDELOH 9809041511', -2.49], ['Sep', '4 Debit Purchase - VISA On 090219 CLEVELAND OH 6100616495', -8.0], ['Sep', '9 Debit Purchase BJS WHOLESALE #0 BEACHWOOD   OH 2109071929', -15.98], ['Sep 16', 'Debit Purchase BJS WHOLESALE #0 BEACHWOOD   OH 5409131828', -17.47], ['Sep 16', 'Debit Purchase ALDI 63047 NORTH RANDELOH', -55.17], ['Sep 16', 'ATM Withdrawal US BANK EMERY RI WARRENSVL HT OH', -80.0], ['Aug 19', 'Debit Purchase - VISA On 081619 844-3018362  NY 0900014115 $', -76.13], ['Aug 19', 'Debit Purchase - VISA On 081619 678-8234713  GA 8103301660', -131.25], ['Aug 20', 'Debit Purchase - VISA On 081719 ORLANDO FL 0100931885', -6.0], ['Aug 20', 'Debit Purchase - VISA On 081719 800-806-6453 OR 9004024610', -113.4], ['Aug 20', 'Debit Purchase - VISA On 081719 ORLANDO FL 0152307616', -166.74], ['Aug 23', 'ATM Withdrawal US BANK EMERY RI WARRENSVL HT OH $', -40.0], ['Aug 23', 'Debit Purchase CLE CRIM FINE WA CLEVELAND   OH', -95.0], ['Aug 26', 'Debit Purchase - VISA On 082419 CLEVELAND OH 7000000822', -2.5], ['Aug 26', 'Debit Purchase - VISA On 082319 800-487-4567 NE 6100121767', -3.95], ['Aug 26', 'Debit Purchase - VISA On 082319 8774174551 CA 5854234444', -20.0], ['Aug 26', 'Debit Purchase OFFICE MAX/OFFI  BEACHWOOD   OH 4608251526', -45.4], ['Aug 26', 'Debit Purchase WM SUPERC Wal-Ma SOUTH EUCLIDOH', -68.27], ['Aug 26', 'Debit Purchase - VISA On 082319 844-3018362  NY 7900014723', -76.13], ['Aug 26', 'Debit Purchase - VISA On 082319 925-855-5000 OH 6100121767', -644.0], ['Aug 27', 'Debit Purchase - VISA On 082619 EUCLID OH 9400186000', -5.11], ['Aug 27', 'Debit Purchase - VISA On 082619 CLEVELAND OH 8894348208', -13.5], ['Aug 28', 'Debit Purchase SHELL SERVICE S  EUCLID      OH', -8.13], ['Aug 28', 'Debit Purchase - VISA On 082719 8774174551 CA 9740238945', -35.5], ['Aug 29', 'Debit Purchase - VISA On 082919 EUCLID OH 1000000434', -9.89], ['Aug 29', 'Debit Purchase - VISA On 082819 800-967-8526 AZ 0100920845', -153.95], ['Sep', '3 Debit Purchase - VISA On 083019 CLEVELAND OH 3400798000', -6.25], ['Sep', '3 Debit Purchase FAMILY DOLLAR #  CLEVELAND   OH', -6.6], ['Sep', '3 Debit Purchase - VISA On 090119 EUCLID OH 5837008882', -7.45], ['Sep', '3 Debit Purchase SHELL SERVICE S  EUCLID      OH', -7.72], ['Sep', '3 Debit Purchase - VISA On 083019 CLEVELAND OH 2855410671', -8.0], ['Sep', '3 Debit Purchase - VISA On 090119 NORTH RANDAL OH 4500566598', -25.45], ['Sep', '3 Debit Purchase - VISA On 083019 CLEVELAND OH 2900019600', -27.97], ['Sep', '3 Debit Purchase - VISA On 083019 844-3018362  NY 4900015332', -76.13], ['Sep', '5 Debit Purchase - VISA On 090419 8774174551 CA 7740218328', -50.0], ['Sep', '9 Debit Purchase - VISA On 090619 844-3018362  NY 1900016045', -76.13], ['Sep 11', 'Debit Purchase - VISA On 091019 8774174551 CA 3740311433', -35.25], ['Sep 17', 'Debit Purchase - VISA On 091619 8774174551 CA 9854238406', -35.0], ['Sep', '3 Debit Purchase - VISA On 090219 BEACHWOOD OH 6100550998 $', -45.19], ['Sep', '4 Debit Purchase - VISA On 090319 CLEVELAND OH 7400000101', -17.66], ['Sep', '5 ATM Withdrawal US BANK EMERY RI WARRENSVL HT OH', -60.0], ['Sep', '5 ATM Withdrawal 26051 EUCLID AVE EUCLID OH', -62.5], ['Sep', '6 Debit Purchase - VISA On 090519 BEDFORD OH 9001303360', -15.0], ['Sep', '9 Debit Purchase - VISA On 090619 866-255-1857 OH 0000796040', -4.95], ['Sep', '9 Debit Purchase - VISA On 090719 CLEVELAND OH 1900019000', -8.0], ['Sep', '9 Debit Purchase FAMILY DOLLAR #  CLEVELAND   OH', -10.67], ['Sep', '9 Debit Purchase - VISA On 090719 WARRENSVILLE OH 0091045000', -10.78], ['Sep', '9 Debit Purchase - VISA On 090719 WARRENSVILLE OH 1200788201', -13.9], ['Sep', '9 Debit Purchase EUCLID MINI MART EUCLID      OH', -21.25], ['Sep', '9 Debit Purchase - VISA On 090619 800-345-7669 CA 9100603964', -26.99], ['Sep', '9 Debit Purchase - VISA On 090619 866-255-1857 OH 0000796040', -165.0], ['Sep', '9 Debit Purchase - VISA On 090719 800-967-8526 AZ 0100162663', -288.27], ['Sep 11', 'Debit Purchase - VISA On 091119 EUCLID OH 4091541000', -20.25], ['Sep 11', 'Debit Purchase - VISA On 091019 WARRENSVL HT OH 3500442097', -25.0], ['Sep 11', '', 542.15, 451.6, 87.92], ['Sep 12', '3', 256.01, 240.84, 76.11], ['Sep 13', '4', 1021.32, 212.69, 914.43], ['Sep 16', '5', 241.07, 37.69, 73.15], ['Sep 17', '6', 228.4, 856.0, 46.86], ['Sep 18', '9', 185.83, 214.08, 35.86], ['Aug 29', '', 21.99], ['Sep 11', 'Debit Purchase - VISA On 090919 NORTH ROYALT OH 3249502295', -49.66], ['Sep 12', 'Debit Purchase - VISA On 091019 EUCLID OH 4837003369', -4.77], ['Sep 12', 'Debit Purchase EUCLID MINI MART EUCLID      OH 1109121527', -7.04], ['Sep 13', 'Debit Purchase - VISA On 091219 Euclid OH 5100391587', -19.5], ['Sep 16', 'Debit Purchase K AND F OIL COMP CLEVELAND   OH 5009141204', -3.46], ['Sep 16', 'Debit Purchase - VISA On 091319 678-8234713  GA 6274201304', -131.25], ['Sep 16', 'Debit Purchase - VISA On 091419 800-639-6111 KS 7100348442', -553.93], ['Sep 17', 'Debit Purchase - VISA On 091619 TWINSBURG OH 9720216966', -5.07], ['Sep 17', 'Debit Purchase - VISA On 091519 EUCLID OH 9002059593', -6.22], ['Sep 18', 'Debit Purchase EUCLID MINI MART EUCLID      OH 9609180804', -9.0], ['Sep 18', 'Paper Statement Fee 1800006037', -2.0]]


    n = negative_days_count(ad, ded, -39.44)
    print(n)

