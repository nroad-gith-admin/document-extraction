import fitz,os, re
from unidecode import unidecode

class ExtractElectronics:
    def __init__(self, filepath):
        if type(filepath)!= str:
            raise TypeError("Expecting type should be str")
        if not os.path.isfile(filepath):
            raise FileNotFoundError(filepath)
        self.filepath = filepath
        try:
            self.doc = fitz.open(filepath)
        except:
            Exception("Failed to load the file: "+str(filepath))

    def num_page(self):
        return self.doc.pageCount
    def get_metadata(self):
        return self.doc.metadata

    def read_page(self, pageNums, typeOut="text"):
        '''
        "text": (default) plain text with line breaks. No formatting, no text position details, no images.
        "blocks": generate a list of text blocks (= paragraphs).
        "words": generate a list of words (strings not containing spaces).
        "html": creates a full visual version of the page including any images. This can be displayed with your internet browser.
        "dict" / "json": same information level as HTML, but provided as a Python dictionary or resp. JSON string. See TextPage.extractDICT() resp. TextPage.extractJSON() for details of its structure.
        "rawdict": a super-set of TextPage.extractDICT(). It additionally provides character detail information like XML. See TextPage.extractRAWDICT() for details of its structure.
        "xhtml": text information level as the TEXT version but includes images. Can also be displayed by internet browsers.
        "xml": contains no images, but full position and font information down to each single text character. Use an XML module to interpret.
        :param pageNums:
        :param typeOut:
        :return:
        '''
        if "text" not in typeOut and \
                "blocks" not in typeOut and \
                "words" not in typeOut and \
                "html" not in typeOut and \
                "dict" not in typeOut and \
                "json" not in typeOut and \
                "xhtml" not in typeOut and \
                "xml" not in typeOut:
            raise Exception("Expecting typeOut either text, blocks, words, html, dict, json, xhtml or xml")
        data = []
        if type(pageNums) == str:
            if "all" in pageNums:
                pageNums = list(range(self.num_page()))
        if type(pageNums) != list:
            raise TypeError("Expecting pageNum should be int")
        for pageNum in pageNums:
            if pageNum> self.num_page():
                raise Exception("Page Number not found: "+str(pageNum))

            page = self.doc[pageNum]
            text = page.getText(typeOut)
            data.append(text)

        return data

    def search_text(self, searchTerm, pageNums, hitArea=16):
        '''
            searchTerm: query to be search for
            hitArea: This delivers a list of up to 16 rectangles
        '''
        data = []
        if type(pageNums) != list:
            raise TypeError("Expecting pageNum should be int")
        for pageNum in pageNums:
            if pageNum> self.num_page():
                raise Exception("Page Number not found: "+str(pageNum))
            page = self.doc[pageNum]
            areas = page.searchFor(searchTerm, hitArea)
            data.append(areas)

        return data

    def close(self):
        self.doc.close()



    def remove_non_ascii(self,text):
        return "".join(i for i in text if ord(i) < 128)
    def is_electronicsPdf(self):
        meta = self.get_metadata()
        data = "".join(self.read_page("all")).replace("\n","").strip()
        data = re.sub(r'[^\x00-\x7F]+', ' ', data)

        data = self.remove_non_ascii(data).strip()
        if len(data)>0:
            return True
        return False



if __name__ == "__main__":
    # filepath = r"/Users/prasingh/Prashant/Prashant/CareerBuilder/Extraction/data/BS_NT/BS_JPMC"
    # files = [os.path.join(filepath,i) for i in os.listdir(filepath)]
    # for file in files:
    #     try:
    #         obj = ExtractElectronics(file)
    #         numPage = obj.num_page()
    #         metadata = obj.get_metadata()
    #         data = obj.read_page("all","blocks")
    #         # data = [i for i in data if i[-3].strip()!='']
    #         print( data)
    #     except:
    #         print(file)

    #
    filepath = r"/Users/prasingh/Prashant/Prashant/CareerBuilder/Extraction/data/BS_NT/BS_PNC/0064O00000kBOB5QAO-00P4O00001JkMbmUAF-shawn_frick_last_60_days_of_ba.pdf"
    extractElecObj = ExtractElectronics(filepath)
    numPage = extractElecObj.num_page()
    data = []
    for i in list(range(numPage)):
        data.extend(extractElecObj.read_page(pageNums=[i, ], typeOut='words'))

    # data = [str(i[-3]) for i in data if str(i[-3]).strip() != '']
    # newData = []
    # for d in data:
    #     newData.extend(d.split("\n"))
    # data = newData
    # for d in data:
    print(data)
    # format1Headers = ["Date", "Description", "Amount"]
    # format1Headers = "".join(format1Headers).lower()
    # for d in data:
    #     if "".join(d