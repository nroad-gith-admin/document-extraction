import configparser,os
import sys, os
curpath = os.path.join(os.path.dirname(os.path.realpath(__file__)))
sys.path.insert(0, curpath)



config_file_loc = os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "..", "config", "bankstatement.cfg")
config_obj = configparser.ConfigParser()



try:
    config_obj.read(config_file_loc)
    account = (config_obj.get("JPMC", "account"))
    routing = (config_obj.get("JPMC", "routing"))
    accountname = (config_obj.get("JPMC", "name"))


except Exception as e:
    raise Exception("Config file error: " + str(e))


# print(account,routing,begbal,deposit,withdraw,endbal)


class ExtractJPMC:


    def get_classified(self, data):
        self.data = data
        self.extractedData = {}
        try:
            accountNum = self.extract_account()
            if accountNum != None:
                self.extractedData["ACCOUNTNUM"] = {accountNum: 1}
        except:
            pass

        try:
            routingNum = self.extract_routing()
            if routingNum != None:
                self.extractedData["ROUTINGNUM"] = {routingNum: 1}
        except:
            pass

        try:
            name = self.extract_name()
            if name != None:
                self.extractedData["ACNTHOLDNAME"] = {name: 1}
        except:
            pass

        self.extractedData["BANKNAME"]  ={"JPMorgan Chase Bank":1}
        return self.extractedData

    def extract_account(self):
        account_number = None
        for di, d in enumerate(self.data):
            if account in d:
                d = d.split(account)
                account_number = d[-1]

                break
        return account_number

    def extract_routing(self):
        routing_number = None
        for d in self.data:
            if routing in d:
                routing_number = d.partition(routing)[2].split()[0]
                break
        return routing_number

    def extract_name(self):
        name = None
        flag=False
        for d in self.data:
                if accountname in d:
                    flag=True
                else:
                    if flag==True:
                        name = d.split("NEWLINE")
                        name = [i for i in name if i.strip()!='']
                        name = name[1]
                        flag = False
                        break
        return name





if __name__ == "__main__":
    pathFiles = r"/Users/prasingh/Prashant/Prashant/CareerBuilder/Extraction/data/BS_NT/BS_BOA"
    pathFiles = r"/Users/prasingh/Prashant/Prashant/CareerBuilder/Extraction/data/BankStatementPDF"
    # files = os.listdir(pathFiles)
    # for file in files:
    #     print(file)
    #     file = os.path.join(pathFiles,file)
    #     # print(text)
    #     wellsfargo_obj = ExtractWellsFargo()
    #     data = wellsfargo_obj.get_classified(file)
    #     print(data)
    #     print("----------------------------")

    file = r"0064O00000jtnaiQAA-00P4O00001JjHJUUA3-__last_60_days_of_bank_stateme.pdf"
    file = os.path.join(pathFiles, file)
    wellsfargo_obj = ExtractJPMC()
    data = wellsfargo_obj.get_classified(file)
    print(data)
