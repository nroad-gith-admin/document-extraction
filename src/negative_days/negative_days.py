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
        pass
    try:
        allCols = [[datetime.strptime(i[0],'%m/%d' ),i[-2],i[-1]] for i in allCols]
    except:
        pass

    try:
        allCols = [[datetime.strptime(i[0],'%b %d' ),i[-2],i[-1]] for i in allCols]
    except:
        pass
    return allCols


def negative_days_count(depositCol, withdrawCol, begBalance):
    print(depositCol)
    print(withdrawCol)
    count = 0
    allCols = []
    depositCol = [[i[0],format_amount(i[-1]), 1] for i  in depositCol]
    withdrawCol = [[i[0],format_amount(i[-1]) , -1] for i  in withdrawCol]
    allCols.extend(depositCol)
    allCols.extend(withdrawCol)
    data = sortDate(allCols)
    sortedD = sorted(data, key=lambda x: x[0])

    for i in sortedD:
        if i[-1] == 1:
            begBalance = begBalance+i[-2]

        else:
            begBalance = begBalance-i[-2]

        if begBalance < 0:
            count = count + 1

    return count




if __name__ =="__main__":
    ad =[['Aug 21', 'Federal Benefit Deposit From SSA  TREAS 310 $', 1473.1], ['Sep 18', 'Paper Statement Fee Reversal 1800000931', 2.0], ['Sep 18', 'Federal Benefit Deposit From SSA  TREAS 310', 1473.1]]

    ded = [['Aug 21', 'Debit Purchase WAL-MART #5433 HOT SPRINGS AR $', -21.47], ['Aug 21', 'Debit Purchase WM SUPERC Wal-Ma HOT SPRINGS AR', -337.24], ['Aug 23', 'Debit Purchase - VISA On 082119 HOT SPRINGS  AR 4548491013', -25.01], ['Aug 26', "Debit Purchase LOWE'S #597 HOT SPRINGS AR 0808231850", -22.02], ['Aug 26', "Debit Purchase LOWE'S #597 HOT SPRINGS AR 4308231839", -22.36], ['Aug 26', 'Debit Purchase - VISA On 082319 HOT SPRINGS  AR 6666164034', -55.94], ['Aug 28', 'Debit Purchase WM SUPERC Wal-Ma HOT SPRINGS AR', -13.8], ['Aug 28', 'Debit Purchase WM SUPERC Wal-Ma HOT SPRINGS AR', -72.0], ['Aug 28', 'Debit Purchase Wal-Mart Super C HOT SPRINGS AR', -75.49], ['Aug 29', 'Debit Purchase - VISA On 082819 HOT SPRINGS  AR 0900017200', -25.5], ['Sep', '5 Debit Purchase - VISA On 090319 HOT SPRINGS  AR 7200454887', -34.18], ['Sep 10', 'Debit Purchase Wal-Mart Super C HOT SPRINGS AR', -114.05], ['Sep 11', 'Debit Purchase - VISA On 090919 HOT SPRINGS  AR 3548474023', -14.79], ['Aug 22', 'Electronic Withdrawal To CARDMEMBER SERV $', -62.64], ['Aug 26', 'Electronic Withdrawal To JCPenney CC', -21.9], ['Aug 26', 'Electronic Withdrawal To Entergy Services', -141.38], ['Aug 28', 'Electronic Withdrawal To CAPITAL ONE', -88.83], ['Aug 29', 'Electronic Withdrawal To HSN', -34.0], ['Aug 30', 'Electronic Withdrawal To LIBERTY MUTUAL', -17.81], ['Sep', '4 Electronic Withdrawal To S USA LIFE INS', -141.06], ['Sep', '5 Electronic Withdrawal To CARDMEMBER SERV', -4.95], ['Sep', '6 Electronic Withdrawal To 657851290 ADD', -3.3], ['Sep 13', 'START Scheduled Transfer Transfer 1300000562', -25.0], ['Sep 18', 'Paper Statement Fee 1800000930', -2.0], ['Sep 18', 'Electronic Withdrawal To CARDMEMBER SERV', -105.21]]


    n = negative_days_count(ad, ded, 0, None)
    print(n)

