import pymupdf as pdf
import re
import pathlib as path
import phonenumbers
import exception

text = [] #for storing the text of the file
github_pattern = r'(?i)github\.com\/([a-z\d](?:[a-z\d]|-(?=[a-z\d])){0,38})'
linkedin_pattern = r'(?i)linkedin\.com\/in\/([a-z0-9\-]{3,100})\/?'
email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'

def extract_text(file):
    try:
        #storing the text inside the text array
        with pdf.open(filename= file)as doc:
            for page in doc:
                text.append(page.get_text())
                
    except FileNotFoundError:
        raise FileNotFoundError
    except pdf.EmptyFileError:
        raise exception.FileIsEmpty
    except pdf.FileDataError:
        raise exception.FileContentCorrupted
    
def extract_links():
    try:
        github = re.findall(github_pattern, text)
        linkedin = re.findall(linkedin_pattern, text)
        email = re.findall(email_pattern, text)
        phoneno = phonenumbers.phonenumbermatcher(text, "IN")
    except:
    
    
    