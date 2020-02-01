import configparser,os
import sys, os
curpath = os.path.join(os.path.dirname(os.path.realpath(__file__)))
sys.path.insert(0, curpath)

from imageTextExtractor import ImageTextExtractor
from PIL import Image
from pdf2image import convert_from_path

image_block_obj = ImageTextExtractor()


config_file_loc = os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "..", "config", "bankstatement.cfg")
config_obj = configparser.ConfigParser()



try:
    config_obj.read(config_file_loc)
    account = (config_obj.get("PNC", "account"))
    routing = (config_obj.get("PNC", "routing"))


except Exception as e:
    raise Exception("Config file error: " + str(e))


# print(account,routing,begbal,deposit,withdraw,endbal)


class ExtractPNC:


    def get_classified(self, data):
        # print(data)
        self.data = data
        self.extractedData = {}

        try:
            accountNum,name = self.extract_account()
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

        # name = self.extract_name()

        if name != None:
            self.extractedData["ACNTHOLDNAME"] = {name: 1}

        self.extractedData["BANKNAME"]  ={"PNC Bank":1}
        return self.extractedData

    def extract_account(self):
        account_number = None
        name = None
        for d in self.data[:5]:
            if account.lower() in d.lower():
                d = d.split("NEWLINE")
                d = [i for i in d if i.strip()!=""]
                name = d[1]
                account_number = d[2]
                # d = [i.strip() for i in d if i.strip()!='' and "Primary Account Number:" in i.strip()]
                account_number = account_number.lower().replace(account.lower(),"").strip()
                break
        return account_number,name

    def extract_routing(self):
        routing_number = None
        for d in self.data:
            if routing in d:
                routing_number = d.partition(routing)[2].split()[0]
                break
        return routing_number

    def extract_name(self):
        name = self.data[1]
        for d in self.data[:5]:
            if account in d:
                d = d.split("NEWLINE")
                d = [i for i in d if i.strip()!='']

                ind = [d.index(i) for i in d if i.strip()!='' and "Primary Account Number:" in i.strip()]
                if len(ind)>0:
                    if ind[0]>0:
                        name = d[ind[0]-1].strip()
                break

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
    pathFiles = r"/Users/prasingh/Prashant/Prashant/CareerBuilder/Extraction/data/BS_NT/BS_PNC"
    # files = os.listdir(pathFiles)
    # for file in files:
    #     print(file)
    #     file = os.path.join(pathFiles,file)
    #     # print(text)
    #     PNC_obj = ExtractPNC()
    #     data = PNC_obj.get_classified(file)
    #     print(data)
    #     print("----------------------------")

    file = r"0064O00000kBOB5QAO-00P4O00001JkMbIUAV-shawn_frick_last_60_days_of_ba.pdf"
    file = os.path.join(pathFiles, file)
    PNC_obj = ExtractPNC()
    data = PNC_obj.get_classified(file)
    print(data)
