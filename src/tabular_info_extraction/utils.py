import re,os
from pdf2image import convert_from_path


def check_table_inside_table(t1, t2):
    t1_min_val = t1.cells[0][0]
    t1_max_val = t1.cells[-1][-1]

    t2_min_val = t2.cells[0][0]
    t2_max_val = t2.cells[-1][-1]

    if t1_min_val.x1 == t2_min_val.x1 \
            and t1_min_val.y2 == t2_min_val.y2 \
            and t1_max_val.x2 == t2_max_val.x2 \
            and t1_max_val.y1 == t2_max_val.y1:
        return True

    if t1_min_val.x1 >= t2_min_val.x1 \
            and t1_min_val.y2 <= t2_min_val.y2 \
            and t1_max_val.x2 <= t2_max_val.x2 \
            and t1_max_val.y1 >= t2_max_val.y1:
        return True
    return False



def df_to_list( df):
    newli = []
    for di in list(df):
        di = str(di)
        if '\n' in di:
            newli.extend(di.split('\n'))
        else:
            newli.append(di)

    return newli


def clean_pandas(df_col):
    if re.search('^(-*)$', df_col):
        pos = re.search('^(-*)$', df_col).start()
        return df_col[:pos]
    else:
        return df_col


def convert_pdf_images(filepath):
    if os.path.isfile(filepath) ==False:
        raise Exception("File not found error: "+str(filepath))
    folder = "working"
    if os.path.isdir("working")==False:
        os.makedirs("working")

    pages = convert_from_path(filepath)
    for pagenum, page in enumerate(pages):
        newfilename_temp = str(pagenum) + ".jpg"
        page.save(os.path.join("working", newfilename_temp), 'JPEG')


