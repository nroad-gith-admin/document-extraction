from imageTextExtractor import ImageTextExtractor
from pdf2image import convert_from_path
from PIL import Image
import os,re
image_block_obj = ImageTextExtractor()



def convert_pdf_images(filepath, pagenum):
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

        pages = convert_from_path(filepath)
        for pgn, page in enumerate(pages):
            # print(page)
            if pgn in pagenum:
                newfilename_temp = str(pgn) + ".jpg"
                page.save(os.path.join("working", newfilename_temp), 'JPEG')
                path_img.append(os.path.join("working", newfilename_temp))
        contents_pdf = []

        for imagefiles in path_img:
            imagefiles = Image.open(imagefiles)
            text_seg = image_block_obj.process_image(imagefiles)
            text_seg = text_seg.split("\n")
            text_seg = [i for i in text_seg if i != '']
            # text_seg = text_seg[:upto_blocks]
            contents_pdf.extend(text_seg)
    except Exception as e:
        raise Exception("Failed in convert_pdf_images. Reason: " + str(e))
    return contents_pdf

def isBankStatement(data):
    params = {}
    if re.search(r"\b" + "us bank" + r"\b", data.lower()):
        params["documentType"] = "bank statement"
        params["params"] = {}
        params['params']["bankname"] = "US Bank"
        params['params']["columns"] = (1,2,2)
        return params
    elif re.search(r"\b" + "wells fargo" + r"\b", data.lower()):
        params["documentType"] = "bank statement"
        params["params"] = {}
        params['params']["bankname"] = "wells fargo"
        params['params']["columns"] = (2, 3, 4)
        return params

    elif re.search(r"\b" + "bank of america" + r"\b", data.lower()) or re.search(r"\b" + "bkofamerica" + r"\b", data.lower()):
        params["documentType"] = "bank statement"
        params["params"] = {}
        params['params']["bankname"] = "bank of america"
        params['params']["columns"] = (1, 2, 2)
        return params
    elif re.search(r"\b" + "chase bank" + r"\b", data.lower()):
        params["documentType"] = "bank statement"
        params["params"] = {}
        params['params']["bankname"] = "jpmorgan chase bank"
        params['params']["columns"] = (1, 2, 2)
        return params
    elif re.search(r"\b" + "usbank.com" + r"\b", data.lower()):
        params["documentType"] = "bank statement"
        params["params"] = {}
        params['params']["bankname"] = "us bank"
        params['params']["columns"] = (1, 2, 2)
        return params

    elif re.search(r"\b" + "pnc bank" + r"\b", data.lower()):
        params["documentType"] = "bank statement"
        params["params"] = {}
        params['params']["bankname"] = "pnc bank"
        params['params']["columns"] = (2, 1, 1)
        return params

    else:
        return None



def isW2(data):
    params = {}
    if re.search(r"\b" + "Employee’s social security number".lower() + r"\b", data.lower()) or \
        re.search(r"\b" + 'Employer identification number'.lower()  + r"\b", data.lower()) or \
        re.search(r"\b" + "Wages, tips, other compensation".lower() + r"\b", data.lower()) or\
        re.search(r"\b" +  "Social security wages".lower()+ r"\b", data.lower()) or\
        re.search(r"\b" + "Social security wage".lower() + r"\b", data.lower()):
            params["documentType"] = "w2"
            params["params"] = {}
            return params
    return None

def extractData(pdfPath):
    try:
        data = (convert_pdf_images(pdfPath, [0,1, ]))
        data = " ".join(data).lower()
        # print(data)
        isBankSt = isBankStatement(data)
        if isBankSt!=None:
            return isBankSt
        else:
            isw2Data = isW2(data)
            if isw2Data != None:
                return isw2Data
        return {}
    except Exception as e:
        return {}

# print(isBankStatement("us bank data statement statement"))
# print(isW2("w2 data statement statement"))

if __name__=="__main__":
    # import csv
    #
    # csvwriter = csv.writer(open("ClassifierResult3.csv","w",newline=""))
    # filepath=r"/Users/prasingh/Prashant/Prashant/CareerBuilder/Extraction/data/classifier_testing3"
    # files= os.listdir(filepath)
    # for f in files:
    #     d = extractData(os.path.join(filepath,f))
    #     if 'documentType' in d:
    #         csvwriter.writerow((f,d['documentType']))
    #     else:
    #         csvwriter.writerow((f,None))


    # d = extractData(r"/Users/prasingh/Prashant/Prashant/CareerBuilder/Extraction/data/BankStatementPDF/0060B00000ihIGEQA2-00P4O00001KoCcaUAF-Stacy Owens Oct BS.pdf")
    # d = extractData(r"/Users/prasingh/Prashant/Prashant/CareerBuilder/Extraction/data/BS_NT/BS_BOA/0064O00000k7RiOQAU-00P4O00001KTl0PUAT-__last_60_days_of_bank_stateme.pdf")
    d = extractData(r"/Users/prasingh/Prashant/Prashant/CareerBuilder/pdftablereader/Bank_Statement_Parser/BankStatementParser/main/TableExtractor/bank_statements/PNCBANK/2016/10903793305217012000/Aug cc (2).pdf")
    print(d)

