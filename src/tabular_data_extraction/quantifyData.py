import sys, os

curpath = os.path.join(os.path.dirname(os.path.realpath(__file__)))
sys.path.insert(0, curpath)
import re

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

def getFormatted(data):
    data = df_to_list(data)
    data = [i.strip() for i in data if i.strip()!='']
    date = None
    amounts = []
    description = []
    if isDate(data[0]):
        for i in data:
            if isDate(i):
                date = i
            elif isAmount(i):
                amounts.append(i)
            else:
                description.append(i)

    if date!=None and len(amounts)>0:
        return date, amounts, description
    else:
        return None,None,None

def isPartDescription(data):
    data = df_to_list(data)
    data = [i.strip() for i in data]
    if data[0]=="":
        data = [i.strip() for i in data if i.strip()!='']

        if len(data)==1 :
            data = data[0]
            if not isDate(data) and not isAmount(data):
                return True
    return False

def get_all_formatted( data):
    newdata = []
    flag = False
    for iData in data:
        try:
            date, amount, des = getFormatted(iData)
            if date!=None and amount!=None and des!=None:
                tempList = []
                tempList.append(date)
                tempList.append(" ".join(des))
                tempList.extend(amount)
                newdata.append(tempList)
                flag = True
            elif isPartDescription(iData) and flag==True:
                iData = [i.strip() for i in iData if i.strip() != '']
                newdata[-1][1] = newdata[-1][1]+" "+iData[0]
        except:
            pass

    return newdata






if __name__ == "__main__":
    # print(isDate("$24.24"))
    print(isAmount("141.81-"))
    # date,amount,des = getFormatted(["Aug 26\nDebit Purchase\nLOWE'S #597 HOT SPRINGS AR", '4308231839','46.44', '22.36-'])
    # print(date,amount,des)
    # print(get_all_formatted([["Aug 26\nDebit Purchase\nLOWE'S #597 HOT SPRINGS AR", '4308231839','46.44', '22.36-'],["","fsdjfksdj"]]))