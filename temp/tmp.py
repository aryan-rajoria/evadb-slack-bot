import os
import pandas as pd
from pdfdocument.document import PDFDocument

# def load_pdf_into_eva (cursor, doc_name):
#     try:
#         cursor.query("""LOAD PDF '""" + doc_name + """' INTO OMSCSPDFTable""").df()
#     except Exception:
#         return False
#     return True

def load_slack_dump(cursor):
    if ("slack_dump" in os.listdir(".")):
        path = "./slack_dump/"
        pdf_path = "./slack_dump_pdfs/"
        if not os.path.exists(pdf_path):
            print("Creating dir `" + pdf_path + "` for slack dump PDFs")
            os.makedirs(pdf_path)
        slackDumpFiles = os.listdir(path)
        slackDumpPDFFiles = os.listdir(pdf_path)
        df = pd.DataFrame()

        # Change pwd to output dir
        os.chdir(pdf_path)
        load_counter = 0
        total_counter = 0
        for file, i in zip(slackDumpFiles, range(len(slackDumpFiles))):
            total_counter += 1
            if file.endswith(".json"):
                pdf_name = "SlackDump" + str(i+1) + ".pdf"
                if pdf_name not in slackDumpPDFFiles:
                    pdf = PDFDocument(pdf_name)
                    pdf.init_report()
                    df1 = pd.read_json("../" + path + file)
                    # df = pd.concat([df, df1[df1.columns.intersection(set(['client_msg_id', 'type', 'user', 'text', 'ts']))]])
                    df = pd.concat([df, df1[df1.columns.intersection(set(['text']))]])
                    pdf.p(df.to_csv(index=False))
                    pdf.generate()
                # if load_pdf_into_eva (cursor, pdf_name):
                #     load_counter += 1
            if load_counter>10:
                break

        os.chdir("./../")
        # we can skip for one of the following reasons:
        # 1. PDF was already in the table, so no need to load
        # 2. Input file was not in a JSON format
        print(str(load_counter), " new PDFs loaded, skipped " + str(total_counter - load_counter))


import evadb

c = evadb.connect().cursor()
load_slack_dump(c)