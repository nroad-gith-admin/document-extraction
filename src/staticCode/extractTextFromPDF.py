from imageTextExtractor import ImageTextExtractor
from PIL import Image
import os
from pdf2image import convert_from_path
from wellsfargo_static import ExtractWellsFargo
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



if __name__ == "__main__":
    pathFiles = r"/Users/prasingh/Prashant/Prashant/CareerBuilder/Extraction/data/BS_NT/BS_WF"
    # files = os.listdir(pathFiles)
    # for file in files:
    #     print(file)
    #     file = os.path.join(pathFiles,file)
    #     # print(text)
    #     wellsfargo_obj = ExtractWellsFargo()
    #     data = wellsfargo_obj.get_classified(file)
    #     print(data)
    #     print("----------------------------")


    file = r"0064O00000kBbdOQAS-00P4O00001JkGmEUAV-Victor Lovelace, BS 3.pdf"
    file = os.path.join(pathFiles,file)
    wellsfargo_obj = ExtractWellsFargo()
    data = wellsfargo_obj.get_classified(file)
    print(data)