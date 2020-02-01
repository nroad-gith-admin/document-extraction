from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfpage import PDFTextExtractionNotAllowed
from pdfminer.pdfinterp import PDFResourceManager
from pdfminer.pdfinterp import PDFPageInterpreter
from pdfminer.pdfdevice import PDFDevice
from pdfminer.layout import LAParams
from pdfminer.converter import PDFPageAggregator
import pdfminer
import os,re
# Open a PDF file.

def extract_block_text(filename, pages=[]):
    if not os.path.isfile(filename):
        raise FileNotFoundError(filename)
    with open(filename ,"rb") as fp:
        # Create a PDF parser object associated with the file object.
        parser = PDFParser(fp)

        # Create a PDF document object that stores the document structure.
        # Password for initialization as 2nd parameter
        document = PDFDocument(parser)

        # Check if the document allows text extraction. If not, abort.
        if not document.is_extractable:
            raise PDFTextExtractionNotAllowed

        # Create a PDF resource manager object that stores shared resources.
        rsrcmgr = PDFResourceManager()

        # Create a PDF device object.
        device = PDFDevice(rsrcmgr)

        # BEGIN LAYOUT ANALYSIS
        # Set parameters for analysis.
        laparams = LAParams()

        # Create a PDF page aggregator object.
        device = PDFPageAggregator(rsrcmgr, laparams=laparams)

        # Create a PDF interpreter object.
        interpreter = PDFPageInterpreter(rsrcmgr, device)
        # loop over all pages in the document
        data = []
        if len(pages)==0:
            for page in PDFPage.create_pages(document):
                # read the page into a layout object
                interpreter.process_page(page)
                layout = device.get_result()

                # extract text from this object
                parse_obj(layout._objs, data)
        else:
            for page_i in pages:

                for j,page in enumerate(PDFPage.create_pages(document)):
                    # read the page into a layout object
                    if j+1==page_i:
                        interpreter.process_page(page)
                        layout = device.get_result()

                        # extract text from this object
                        parse_obj(layout._objs, data)
        return data

def parse_obj(lt_objs, data):


    # loop over the object list
    for obj in lt_objs:

        # if it's a textbox, print text and location
        if isinstance(obj, pdfminer.layout.LTTextBoxHorizontal):
            # print ("%6d, %6d, %s" % (obj.bbox[0], obj.bbox[1], obj.get_text().replace('\n', '_')))
            boxData = obj.get_text().replace('\n', ' ')
            boxData = re.sub(' +', ' ', boxData)
            data.append(boxData)
        # if it's a container, recurse
        elif isinstance(obj, pdfminer.layout.LTFigure):
            parse_obj(obj._objs, data)


if __name__ =="__main__":
    data = []
    filepath = "/Users/prasingh/Prashant/Prashant/CareerBuilder/Extraction/data/BS_NT/BS_JPMC"
    files  = os.listdir(filepath)
    for file in files:
        file = os.path.join(filepath,file)
        data = extract_block_text(file)
        data = [i for i in data if i.strip()!='']
        print(data)

