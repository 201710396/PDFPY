import pdf2image
from PIL.ImageQt import ImageQt
from PyQt5.QtGui import *

def filepathToImage(filepath):
    result = []
    images = pdf2image.convert_from_path(filepath)
    
    for i, page in enumerate(images):
        title = "./%s_%d.jpg" % (filepath.split("/")[-1].replace(".pdf", ""), i)
        result.append(title)
        page.save(title, "JPEG")
    
    return result