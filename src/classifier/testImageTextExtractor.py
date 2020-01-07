from imageTextExtractor import ImageTextExtractor
from pdf2image import convert_from_path
from PIL import Image
import os
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

pdfile = r"/Users/prasingh/Prashant/Prashant/CareerBuilder/Extraction/data/classifier_testing2/0064O00000kKXqRQAW-00P4O00001KSLQTUA5-Anita_w2.pdf"
# pdfile = r"/Users/prasingh/Prashant/Prashant/CareerBuilder/Extraction/data/bankofamerica/0064O00000iyGcEQAU-00P4O00001KD5lJUAT-chris_kertesz_last_60_days_of_.pdf"
data = (convert_pdf_images(pdfile,[1,]))
for d in data:
    print(d)