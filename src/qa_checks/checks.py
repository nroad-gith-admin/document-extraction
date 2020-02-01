
pass_message = "Pass"
fail_message = "Fail"

def check_uniqueid(id):
    try:
        # int(id)
        if len(id.strip()) ==18:
            return pass_message
    except:
        return fail_message + ": Value cannot be extracted"
    return fail_message + ": Length is not equal 18"

def check_filename(filename):
    try:
        if len(filename.strip()) >=20:
            return pass_message
    except:
        return fail_message + ": Value cannot be extracted"
    return fail_message + ": Length is less than 20"

def check_accountname(name):
    try:
        if len(name.strip()) >=5:
            return pass_message
    except:
        return fail_message + ": Value cannot be extracted"
    return fail_message + ": Length is less than 5"

def check_bankname(name):
    try:
        if len(name.strip()) >=3:
            return pass_message
    except:
        return fail_message + ": Value cannot be extracted"
    return fail_message+": Length is less than 3"

def check_accountnum(number):
    try:
        if len(number.strip()) >=5:
            return pass_message
    except:
        return fail_message + ": Value cannot be extracted"
    return fail_message + ": Length is less than 5"


def check_specific(number):
    try:
        float(number)
        if float(number)==-9999.99:
            return fail_message+": Value cannot be extracted"
        if len(str(number).strip()) >=0:
            return pass_message
    except:
        return fail_message+": Value cannot be extracted"
    return fail_message + ": Length is less than 0"

def check_all(data):
    data["nameOnTheAccountStatus"] = check_accountname(data["nameOnTheAccount"])
    data["accountNumberStatus"] = check_accountnum(data["accountNumber"])
    data["bankNameStatus"] = check_bankname(data["bankName"])
    data["routingNumberStatus"] = check_specific(data["routingNumber"])
    data["averageDailyBalanceStatus"] = check_specific(data["averageDailyBalance"])
    data["loanDepositsStatus"] = check_specific(data["loanDeposits"])
    data["payrollDepositsStatus"] = check_specific(data["payrollDeposits"])
    data["CCPaymentsStatus"] = check_specific(data["CCPayments"])
    data["loanPaymentsStatus"] = check_specific(data["loanPayments"])
    data["directDepositsStatus"] = check_specific(data["directDeposits"])
    # data["uniqueIdStatus"] = check_uniqueid(data["uniqueId"])
    data["docStatus"] = checkfield(data["accountNumber"], data["nameOnTheAccount"], data["directDeposits"] )

    return data

def checkfield(accnum, accname, directdep):
    directdep = str(directdep)
    try:
        if float(directdep) == -9999.99:
            directdep = ""
    except:
        directdep=""
    if len(accname)>0 and len(accnum)>0 and len(directdep)>0:
        return "SUCCESS"
    elif len(accnum)==0 and len(accname) == 0:
        return fail_message
    elif len(accname)>0 and len(accname)>0:
        return "Partial Success"
    elif len(accname)>0 and len(directdep)>0:
        return "Partial Success"
    elif len(accnum)>0 and len(directdep)>0:
        return "Partial Success"

    return fail_message
