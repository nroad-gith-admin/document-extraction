import sys, os

curpath = os.path.join(os.path.dirname(os.path.realpath(__file__)))
sys.path.insert(0, curpath)
import camelot


class TableExtractorCamelot:
    def extract_table(self, pdfFile, pageNum):

        tables = camelot.read_pdf(pdfFile, pages = str(pageNum),
        flavor = 'stream',
        edge_tol = 85,)
            # pdfFile, pages=str(pageNum),
            #                           flavor='stream',
            #                           edge_tol=250,
            #                       column_tol = 13,
            #                       row_tol = 3
            #                                 )

        return tables


if __name__=="__main__":
    filepath = r"/Users/prasingh/Prashant/Prashant/CareerBuilder/Extraction/data/NEW_BANK/FIFTH THIRD BANK/0064O00000k9tMHQAY-00P4O00001JjrFhUAJ-Sep BS.pdf"
    # filepath = r"/Users/prasingh/Prashant/Prashant/CareerBuilder/pdftablereader/Bank_Statement_Parser/BankStatementParser/main/TableExtractor/bank_statements/PNCBANK_back/t/10915568605217091500/4-28-2017 Operating Statement.pdf"
    # filepath = r"/Users/prasingh/Prashant/Prashant/CareerBuilder/pdftablereader/Bank_Statement_Parser/BankStatementParser/main/TableExtractor/bank_statements/PNCBANK_back/t/20988146275217061400/April Bank.pdf"
    tableCamelotObj = TableExtractorCamelot()
    page = 2
    tables = tableCamelotObj.extract_table(filepath, str(page))
    for table_i in range(len(tables)):
        data = (tables[table_i].df)
    #     print(data)
        for i, d in data.iterrows():
            print(i,list(d))