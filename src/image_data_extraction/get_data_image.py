import sys, os

curpath = os.path.join(os.path.dirname(os.path.realpath(__file__)))
sys.path.insert(0, curpath)

from imageTextExtractor import ImageTextExtractor
from PIL import Image
from pdf2image import convert_from_path
import os

image_block_obj = ImageTextExtractor()


class ExtractDataImage:
    def convert_pdf_images(self, filepath, pagenum):
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

    def get_data(self, filepath, pageNum):
        if type(pageNum)!=list:
            raise Exception("Expecting pageNum in a list")

        data = self.convert_pdf_images(filepath, pageNum)
        return data



if __name__=="__main__":
    tableInfoObj = ExtractDataImage()
    filepath  = r'/Users/prasingh/Prashant/Prashant/CareerBuilder/Extraction/data/BS_NT/BS_PNC/3-31-2017 Operating Statement.pdf'
    data= tableInfoObj.get_data(filepath,[0,1,])
    print("deposit amount: ", data)

