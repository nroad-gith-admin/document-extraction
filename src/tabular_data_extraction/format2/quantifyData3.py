import sys, os

curpath = os.path.join(os.path.dirname(os.path.realpath(__file__)))
sys.path.insert(0, curpath)
import re

additionKeywords = ['Additions',
                         "Deposits",
                         "Refunds",
                    "checking activity"
                         ]
deductionKeywords = ["Deductions",
                          "Purchases",
                          "Service Charges and Fees",
                        "WITHDRAWALS",
                     "subtractions",
                     "Fees"
                          ]
# keywords = [""]
def isDate(val):
    val = val.lower()
    if re.search(r"\b" + "jan" + r"\b", val) or \
        re.search(r"\b" + "feb" + r"\b", val) or \
        re.search(r"\b" + "mar" + r"\b", val) or \
        re.search(r"\b" + "apr" + r"\b", val) or \
        re.search(r"\b" + "may" + r"\b", val) or \
        re.search(r"\b" + "jun" + r"\b", val) or \
            re.search(r"\b" + "jul" + r"\b", val) or\
        re.search(r"\b" + "aug" + r"\b", val) or\
        re.search(r"\b" + "sep" + r"\b", val) or\
        re.search(r"\b" + "oct" + r"\b", val) or\
        re.search(r"\b" + "nov" + r"\b", val) or\
        re.search(r"\b" + "dec" + r"\b", val) or\
        re.search(r"\b" + "january" + r"\b", val) or \
        re.search(r"\b" + "february" + r"\b", val) or \
        re.search(r"\b" + "march" + r"\b", val) or \
        re.search(r"\b" + "april" + r"\b", val) or \
        re.search(r"\b" + "may" + r"\b", val) or \
        re.search(r"\b" + "june" + r"\b", val) or \
        re.search(r"\b" + "july" + r"\b", val) or \
        re.search(r"\b" + "august" + r"\b", val) or \
        re.search(r"\b" + "september" + r"\b", val) or \
        re.search(r"\b" + "october" + r"\b", val) or \
        re.search(r"\b" + "november" + r"\b", val) or \
        re.search(r"\b" + "december" + r"\b", val):
        if len(val)<10:
            return True

    if "/" in val:
        splitVal = val.split("/")
        splitVal = [i.strip() for i in splitVal if i.strip()!='']
        boolIsDigits = [i.isdigit() for i in splitVal ]
        if False in boolIsDigits:
            return False
        return True
    return False


def isAmount(val):
    val = val.lower()
    val = val.replace("$",'')
    val = val.replace("-",'')
    val = val.replace(",",'')

    if "."in val:
        splitVal = val.split(".")
        splitVal = [i.strip() for i in splitVal if i.strip() != '']
        boolIsDigits = [i.isdigit() for i in splitVal]
        if False in boolIsDigits:
            return False
        return True
    return False

def df_to_list( df):
    newli = []
    for di in list(df):
        di = str(di)
        if '\n' in di:
            newli.extend(di.split('\n'))
        else:
            newli.append(di)

    return newli


def format_data(data,dateCol, decCol, depositCol, withdrawCol,  lenAmount):
    data = df_to_list(data)
    date = None
    amounts = []
    description = []
    if isDate(data[dateCol]):
        for i in data:
            if isDate(i):
                date = i
            elif isAmount(i) or i.strip()=='':
                amounts.append(i)
            else:
                description.append(i)
    if (len(amounts))>lenAmount:
        amounts.reverse()
        try:
            amounts.remove(value)
        except:
            pass
        amounts.reverse()
    if date!=None and len(amounts)>0:
        return date, amounts, description
    else:
        return None,None,None

def isPartDescription(data, dateCol = 0,decCol=1):
    data = df_to_list(data)
    data = [i.strip() for i in data]
    if data[dateCol]=="" and data[decCol]!='':
        data = [i.strip() for i in data if i.strip()!='']

        if len(data)==1 :
            data = data[0]
            if not isDate(data) and not isAmount(data):
                return True
    return False





def get_formatted(data, dateCol, desCol, depositCol, withdrawCol, lenAmount, headers,additionKeywords,deductionKeywords ):
    '''IF WE DONT HAVE HEADER IN NEW PAGE'''
    newdataDeduction = []
    newdataAddition = []
    flag = False
    deductionFlag = 0
    additionFlag = 0
    continuousNotMatch = 0
    lastAddedCol = None
    ifHeaderFound = False
    allheaders = []
    for header in headers:
        header = [i.strip().lower() for i in header]
        header = " ".join(header).split()
        header.sort()
        allheaders.append(header)
    for iData in data:
        if continuousNotMatch > 2:
            continuousNotMatch = 0
            deductionFlag = 0
            additionFlag = 0
        tempData = [i.strip().lower() for i in iData if i.strip()!='']
        tempData = df_to_list(tempData)
        tempData = " ".join(tempData).split()


        tempData.sort()

        # if ifHeaderFound != True:
        for key in deductionKeywords:
            if key.lower() in " ".join(iData).lower():
                continuousNotMatch = 0

                deductionFlag = 1
                additionFlag = 0
                break
        else:
            for key in additionKeywords:
                if key.lower() in " ".join(iData).lower():
                    continuousNotMatch = 0
                    deductionFlag = 0
                    additionFlag = 1
                    break
        if deductionFlag == 1 or additionFlag==1:
            for headers in allheaders:
                if "".join(tempData).lower().strip() == "".join(headers).lower().strip():
                    ifHeaderFound = True
            if ifHeaderFound == True:
                try:
                    date, amount, des = format_data(iData,dateCol, desCol, depositCol, withdrawCol, lenAmount )

                    if date != None and amount != None and des != None:
                        if "Ending Balance".strip().lower() not in " ".join(
                            des).lower() and "Beginning Balance".strip().lower() not in " ".join(des).lower():
                            continuousNotMatch = 0

                            tempList = []
                            tempList.append(date)
                            tempList.append(" ".join(des))
                            tempList.extend(amount)
                            if len(additionKeywords)==0 or len(deductionKeywords)==0:
                                if deductionFlag == 1 or additionFlag==1:
                                    if tempList[depositCol]!='':
                                        newTempList = []
                                        if  isAmount(tempList[depositCol]):
                                            newTempList.extend([tempList[0], tempList[1], tempList[depositCol]])
                                            newdataAddition.append(newTempList)
                                            lastAddedCol = 'deposit'
                                    if tempList[withdrawCol]!='':
                                        newTempList = []
                                        if isAmount(tempList[withdrawCol]):
                                            newTempList.extend([tempList[0], tempList[1], tempList[withdrawCol]])
                                            newdataDeduction.append(newTempList)
                                            lastAddedCol = 'withdraw'
                            else:
                                if deductionFlag == 1:
                                    newdataDeduction.append(tempList)
                                    lastAddedCol = 'deposit'
                                elif additionFlag == 1:
                                    newdataAddition.append(tempList)
                                    lastAddedCol = 'withdraw'

                            flag = True
                    elif isPartDescription(iData,dateCol, desCol) and flag == True:
                        continuousNotMatch = 0

                        iData = [i.strip() for i in iData if i.strip() != '']
                        if lastAddedCol!=None and lastAddedCol == 'deposit':
                            newdataAddition[-1][1] = newdataAddition[-1][1] + " " + iData[0]
                        elif lastAddedCol!=None and lastAddedCol == 'withdraw':
                            newdataDeduction[-1][1] = newdataDeduction[-1][1] + " " + iData[0]

                    else:
                        continuousNotMatch = continuousNotMatch + 1
                except:
                    pass

    return newdataAddition, newdataDeduction

def get_all_formatted( data, dateCol, desCol,depositCol, withdrawCol,totalAmountsCol=1, isKeywordsPage=True, headers=None,additionKeywords=[],deductionKeywords=[]):

    return get_formatted(data, dateCol, desCol, depositCol, withdrawCol, totalAmountsCol, headers,additionKeywords,deductionKeywords)








if __name__ == "__main__":
    print(isDate("Beginning Balance on Jul 18"))
    # print(isAmount("141.81-"))
    # date,amount,des = getFormatted(["Aug 26\nDebit Purchase\nLOWE'S #597 HOT SPRINGS AR", '4308231839','46.44', '22.36-'])
    # print(date,amount,des)
    # print(get_all_formatted([["Aug 26\nDebit Purchase\nLOWE'S #597 HOT SPRINGS AR", '4308231839','46.44', '22.36-'],["","fsdjfksdj"]]))