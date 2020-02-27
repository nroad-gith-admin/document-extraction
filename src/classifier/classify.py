from imageTextExtractor import ImageTextExtractor
from pdf2image import convert_from_path
from PIL import Image
import os,re, json
from getblocktextpdf import extract_block_text
from get_logger import GetLogger
image_block_obj = ImageTextExtractor()
# obj = ExtractElectronics()

logfilename = "classifier.log"
debugLevel = 2
loggerobj = GetLogger("Classifier", logfilename, debugLevel)
logger = loggerobj.getlogger()
logger.info("Classifier started")
def convert_pdf_images(filepath, pagenum, documentId):
    path_img = []

    if os.path.isfile(filepath) == False:
        raise Exception("File not found error: " + str(filepath))
    try:
        folder = "working"
        if os.path.isdir("working") == False:
            os.makedirs("working")
        else:
            for the_file in os.listdir(folder):
                file_path = os.path.join(folder, the_file)
                try:
                    if os.path.isfile(file_path):
                        os.unlink(file_path)
                except Exception as e:
                    print(e)


        if (".jpg" in filepath or ".png" in filepath or ".jpeg" in filepath) and ".pdf" not in filepath:
            path_img.append(filepath)
        else:
            pages = convert_from_path(filepath)
            for pgn, page in enumerate(pages):
                if pgn in pagenum:
                    newfilename_temp = str(pgn) + ".jpg"
                    page.save(os.path.join("working", newfilename_temp), 'JPEG')
                    path_img.append(os.path.join("working", newfilename_temp))

        contents_pdf = []

        for imageEter, imagefiles in enumerate(path_img):
            fileimage  = imagefiles
            imagefiles = Image.open(imagefiles)
            text_seg = image_block_obj.process_image(imagefiles)
            text_seg = text_seg.split("\n")
            text_seg = [i for i in text_seg if i != '']
            if not os.path.isdir(os.path.join(os.getcwd(), "data")):
                os.mkdir(os.path.join(os.getcwd(), "data"))
            if not os.path.isdir(os.path.join(os.getcwd(),"data",str(documentId))):
                os.mkdir(os.path.join(os.getcwd(),"data",str(documentId)))
            fileToWrite = (os.path.join(os.getcwd(),"data",str(documentId),str(imageEter)+".json") )
            with open(fileToWrite,"w") as f:
                json.dump(text_seg, f)
            # text_seg = text_seg[:upto_blocks]
            contents_pdf.append(text_seg)

    except Exception as e:
        raise Exception("Failed in convert_pdf_images. Reason: " + str(e))
    return contents_pdf

def isBankStatement(dataAll):
    usbankCount = 0
    wfCount = 0
    boaCount=0
    chaseCount = 0
    pncCount = 0
    for data_i, data in enumerate(dataAll):
        data = " ".join(data).lower()
        data = data.replace("\n"," ")
        params = {}

        # print(data)
        # if not re.search(r"\b" + "account" + r"\b", data.lower()):
        #     return None
        # if not re.search(r"\b" + "Beginning balance".lower() + r"\b", data.lower()):
        #     return None
        usbankCount += len(re.findall(r"\b" + "us bank" + r"\b", data.lower()))
        usbankCount += data.lower().count("u.s.")
        usbankCount += len(re.findall(r"\b" + "usbank.com" + r"\b", data.lower()))
        wfCount += len(re.findall(r"\b" + "wells fargo" + r"\b", data.lower()))
        boaCount += len(re.findall(r"\b" + "bank of america" + r"\b", data.lower()))
        boaCount += len(re.findall(r"\b" + "bkofamerica" + r"\b", data.lower()))
        chaseCount += len(re.findall(r"\b" + "chase bank" + r"\b", data.lower()))
        chaseCount += len(re.findall(r"\b" + "JPMorgan".lower() + r"\b", data.lower()))
        chaseCount += len(re.findall(r"\b" + "chase".lower() + r"\b", data.lower()))
        pncCount += len(re.findall(r"\b" + "pnc bank" + r"\b", data.lower()))
        pncCount += len(re.findall(r"\b" + "pnc.com" + r"\b", data.lower()))
        pncCount += len(re.findall(r"\b" + "pnc" + r"\b", data.lower()))
    # print(usbankCount, wfCount,boaCount, chaseCount, pncCount)
    maxVal = max(usbankCount, wfCount,boaCount, chaseCount, pncCount)
    if maxVal<3:
        return None
    if usbankCount == maxVal:
    # if re.search(r"\b" + "us bank" + r"\b", data.lower()) or re.search(r"\b" + "usbank.com" + r"\b", data.lower()):
        params["documentType"] = "bank statement"
        params["params"] = {}
        params['params']["bankname"] = "US Bank"
        params['params']["columns"] = (1,2,2)
        params["pageNum"] = None

        return params
    # elif re.search(r"\b" + "wells fargo" + r"\b", data.lower()):
    elif wfCount == maxVal:
        params["documentType"] = "bank statement"
        params["params"] = {}
        params['params']["bankname"] = "wells fargo"
        params['params']["columns"] = (2, 3, 4)
        params["pageNum"] = None
        return params
    elif boaCount == maxVal:
    # elif re.search(r"\b" + "bank of america" + r"\b", data.lower()) or re.search(r"\b" + "bkofamerica" + r"\b", data.lower()):
        params["documentType"] = "bank statement"
        params["params"] = {}
        params['params']["bankname"] = "bank of america"
        params["pageNum"] = None
        params['params']["columns"] = (1, 2, 2)
        return params
    elif chaseCount == maxVal:
    # elif re.search(r"\b" + "chase bank" + r"\b", data.lower()):
        params["documentType"] = "bank statement"
        params["params"] = {}
        params['params']["bankname"] = "jpmorgan chase bank"
        params["pageNum"] = None
        params['params']["columns"] = (1, 2, 2)
        return params
    elif pncCount == maxVal:
    # elif re.search(r"\b" + "pnc bank" + r"\b", data.lower()):
        params["documentType"] = "bank statement"
        params["params"] = {}
        params['params']["bankname"] = "pnc bank"
        params['params']["columns"] = (2, 1, 1)
        params["pageNum"] = None
        return params

    else:
        return None
    return None



def isW2(dataAll):
    for data_i, data in enumerate(dataAll):
        data = " ".join(data).lower()
        data = data.replace("\n"," ")
        params = {}
        if re.search(r"\b" + "Employee’s social security number".lower() + r"\b", data.lower()) or \
            re.search(r"\b" + 'Employer identification number'.lower()  + r"\b", data.lower()) or \
            re.search(r"\b" + "Wages, tips, other compensation".lower() + r"\b", data.lower()) or\
            re.search(r"\b" +  "Social security wages".lower()+ r"\b", data.lower()) or\
            re.search(r"\b" + "Social security wage".lower() + r"\b", data.lower()) or \
            re.search(r"\b" + "social security number".lower() + r"\b", data.lower()) or \
            re.search(r"\b" + "w-2 wage and tax".lower() + r"\b", data.lower()):
                params["documentType"] = "w2"
                params["params"] = {}
                params["pageNum"] = data_i
                return params
    return None

def isPayStub(dataAll):

    for data_i, data in enumerate(dataAll):
        data = " ".join(data).lower()
        data = data.replace("\n"," ")
        params = {}
        if re.search(r"\b" + "HOURS AND EARNINGS".lower() + r"\b", data.lower()) or \
                re.search(r"\b" + 'Earnings Statement'.lower() + r"\b", data.lower()) or \
                re.search(r"\b" + "pay stub".lower() + r"\b", data.lower()):
            params["documentType"] = "pay stub"
            params["params"] = {}
            params["pageNum"] = data_i
            return params
        if re.search(r"\b" + 'payslip'.lower() + r"\b", data.lower()) and re.search(r"\b" + 'ytd'.lower() + r"\b", data.lower())or \
                re.search(r"\b" + 'pay slip'.lower() + r"\b", data.lower()) and re.search(r"\b" + 'ytd'.lower() + r"\b",
                                                                                         data.lower()):
            params["documentType"] = "pay stub"
            params["params"] = {}
            params["pageNum"] = data_i

            return params
        countYtd = len(re.findall(r"\b" + "ytd" + r"\b", data.lower()))
        if countYtd >=4:
            params["documentType"] = "pay stub"
            params["params"] = {}
            params["pageNum"] = data_i

            return params
        if re.search(r"\b" + 'pay statement'.lower() + r"\b", data.lower()) and re.search(r"\b" + 'ytd'.lower() + r"\b", data.lower())or \
                re.search(r"\b" + 'Pay type'.lower() + r"\b", data.lower()) and re.search(r"\b" + 'ytd'.lower() + r"\b",
                                                                                         data.lower()):
            params["documentType"] = "pay stub"
            params["params"] = {}
            params["pageNum"] = data_i

            return params
        if re.search(r"\b" + 'pay'.lower() + r"\b", data.lower()) and re.search(r"\b" + 'ytd'.lower() + r"\b", data.lower()) and \
                re.search(r"\b" + 'rate'.lower() + r"\b", data.lower()) and re.search(r"\b" + 'current'.lower() + r"\b",
                                                                                         data.lower()):
            params["documentType"] = "pay stub"
            params["params"] = {}
            params["pageNum"] = data_i
            return params
    return None
def extractData(pdfPath, documentId):

    try:
        import time
        st = time.time()

        # try:
        #     data = extract_block_text(pdfPath)
        # except:
        # if electronicsPdfObj.is_electronicsPdf():
        #     data = electronicsPdfObj.read_page("all")
        #
        # else:
        data = (convert_pdf_images(pdfPath, [0,1,2], documentId))
        folderDataPath = os.path.join(os.getcwd(), "data", str(documentId))
        # data = " ".join(data).lower()
        # data = data.replace("\n"," ")
        isw2Data = isW2(data)
        if isw2Data != None:
            isw2Data["dataPath"] = folderDataPath
            return isw2Data
        else:

            isPayStubData = isPayStub(data)
            if isPayStubData != None:
                isPayStubData["dataPath"] = folderDataPath

                return isPayStubData

            isBankSt = isBankStatement(data)
            if isBankSt != None:
                isBankSt["dataPath"] = folderDataPath
                return isBankSt
        return {}
    except Exception as e:
        logger.error("Get Exception in extractData:" + str(e))
        print(e)
        return {}

if __name__=="__main__":
    import csv
    filepath=r"/Users/prasingh/Prashant/Prashant/CareerBuilder/Extraction/data/BS_NT/BS_WF/"

    csvwriter = csv.writer(open("BOACLASS.csv","w",newline=""))
    files= os.listdir(filepath)
    for i, f in enumerate(files):
        print(f)

        d = extractData(os.path.join(filepath,f),f.replace(".pdf",""))
        print(d)
        if 'documentType' in d:
            csvwriter.writerow((f,d['documentType'],d['pageNum']))
        else:
            csvwriter.writerow((f,None))
        print("------------------------------------")
        # break

    # d = extractData(r"/Users/prasingh/Prashant/Prashant/CareerBuilder/Extraction/data/BankStatementPDF/0060B00000ihIGEQA2-00P4O00001KoCcaUAF-Stacy Owens Oct BS.pdf")
    # d = extractData(r"/Users/prasingh/Prashant/Prashant/CareerBuilder/Extraction/data/Batch4/0064O00000k6JjKQAU-00P4O00001JjW22UAF-Jennifer Posey - BS .pdf","123")
    # d = extractData(os.path.join(filepath,"0064O00000kKi4lQAC-00P4O00001KSZyuUAH-Luis De Leon W2.pdf"))
    # file = "0064O00000lASZwQAO-00P4O00001JxXHWUA3-Sonia w2.pdf"
    # file = os.path.join(filepath,file)
    # d = extractData(file,"avcd")
    #
    # print(d)

