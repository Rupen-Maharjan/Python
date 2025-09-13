from PyPDF2 import PdfMerger
import os 

print("This is a PDF merger program created in Python. We will merge files from the 'store' folder.")

os.chdir(os.path.dirname(os.path.abspath(__file__)))
merger = PdfMerger()

def merge(files):   # now expects a list
    listt = sorted(files)
    path = os.path.join(os.getcwd(), "store")
    if os.path.exists(path):
        for val in listt:   # now val is a filename string
            merger.append(os.path.join(path, val))
        merger.write("merged.pdf")
        merger.close()
    else:
        print("Store folder doesn't exist. Please create and add all PDFs there!")

dirs = [f for f in os.listdir("store") if f.endswith(".pdf")]
merge(dirs)
