import configparser,os
import sys, os
curpath = os.path.join(os.path.dirname(os.path.realpath(__file__)))
sys.path.insert(0, curpath)


config_file_loc = os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "..", "config", "bankstatement.cfg")
config_obj = configparser.ConfigParser()

try:
    config_obj.read(config_file_loc)
    account = (config_obj.get("Citi", "account"))
    routing = (config_obj.get("Citi", "routing"))


except Exception as e:
    raise Exception("Config file error: " + str(e))


# print(account,routing,begbal,deposit,withdraw,endbal)


class ExtractCiti:


    def get_classified(self, pdfPath):
        self.data = data
        self.extractedData = {}
        accountNum = self.extract_account()
        if accountNum != None:
            self.extractedData["ACCOUNTNUM"] = {accountNum: 1}

        routingNum = self.extract_routing()
        if routingNum != None:
            self.extractedData["ROUTINGNUM"] = {routingNum: 1}

        name = self.extract_name()
        if name != None:
            self.extractedData["ACNTHOLDNAME"] = {name: 1}

        self.extractedData["BANKNAME"]  ={"Citi Bank":1}
        return self.extractedData

    def extract_account(self):
        account_number = None
        for d in self.data[:5]:
            if account in d:
                d = d.split()
                d = [i.strip() for i in d if i.strip()!='']

                account_number = d[d.index(account)+1]
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
        name = self.data[1]

                # print(d)
                # list_data = d.partition(account)[2].split()[1:]
                # name = []
                # for  l in list_data:
                #     if l.isupper():
                #         name.append(l)
                #     else:
                #         break
                # name = " ".join(name)
                # break
        return name

    def extract_amounts(self):
        begBal = None
        dep = None
        withdrawl = None
        endBal = None

        for d in self.data:
            if "$" in d:
                d = d.split()
                new_d = []
                flag = 0
                for i in d:
                    if i =="-":
                        flag = 1
                    else:
                        if flag == 1:
                            new_d.append("- "+i)
                            flag=0
                        else:
                            new_d.append(i)
                # print(new_d)

                if len(new_d) == 4:
                    begBal = new_d[0]
                    dep = new_d[1]
                    withdrawl = new_d[2]
                    endBal = new_d[3]
        return begBal,dep, withdrawl, endBal



if __name__ == "__main__":
    pathFiles = r"/Users/prasingh/Prashant/Prashant/CareerBuilder/Extraction/data/BS_NT/BS_Citi"
    files = os.listdir(pathFiles)
    for file in files:
        print(file)
        file = os.path.join(pathFiles,file)
        # print(text)
        Citi_obj = ExtractCiti()
        data = Citi_obj.get_classified(file)
        print(data)
        print("----------------------------")

    # file = r"0064O00000aDmSjQAK-00P4O00001JkSvIUAV-chetrum BS.pdf"
    # file = os.path.join(pathFiles, file)
    # Citi_obj = ExtractCiti()
    # data = Citi_obj.get_classified(file)
    # print(data)
