import camelot


class TableExtractorCamelot:
    def extract_table(self, pdfFile, pageNum, edge_tol=85):

        tables = camelot.read_pdf(pdfFile, pages = str(pageNum),
        flavor = 'stream',
        edge_tol = edge_tol,)
            # pdfFile, pages=str(pageNum),
            #                           flavor='stream',
            #                           edge_tol=250,
            #                       column_tol = 13,
            #                       row_tol = 3
            #                                 )

        return tables


if __name__=="__main__":
    filepath = r"/Users/prasingh/Prashant/Prashant/CareerBuilder/Extraction/data/Batch4/0064O00000k5zlKQAQ-00P4O00001JkXAtUAN-nichelle_butler_last_60_days_o.pdf"

    # filepath = r"/Users/prasingh/Prashant/Prashant/CareerBuilder/Extraction/data/BS_NT/BS_BOA/0064O00000k7RiOQAU-00P4O00001KTl0PUAT-__last_60_days_of_bank_stateme.pdf"
    # filepath = r"/Users/prasingh/Prashant/Prashant/CareerBuilder/pdftablereader/Bank_Statement_Parser/BankStatementParser/main/TableExtractor/bank_statements/PNCBANK_back/t/10915568605217091500/4-28-2017 Operating Statement.pdf"
    # filepath = r"/Users/prasingh/Prashant/Prashant/CareerBuilder/pdftablereader/Bank_Statement_Parser/BankStatementParser/main/TableExtractor/bank_statements/PNCBANK_back/t/20988146275217061400/April Bank.pdf"
    tableCamelotObj = TableExtractorCamelot()
    page = 1
    tables = tableCamelotObj.extract_table(filepath, str(page),edge_tol=85)
    for table_i in range(len(tables)):
        data = (tables[table_i].df)
    #     print(data)
        for i, d in data.iterrows():
            print(i,list(d))