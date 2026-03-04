import pymupdf as pdf
import re
import pathlib as path
import phonenumbers
from Backened.app.exception.resume_exception import ResumeEncryptError, ResumeTextEmpty, ResumeFileNotFound, ResumeFileEmpty, ResumeCorrupted, InvalidTextInputError, LinkExtractionError, ResumeExtractionError

def extract_text(file_path):
    try:
        text = "" #for storing the text of the file
        
        #storing the text inside the text array
        with pdf.open(filename= file_path)as doc:
            # checking if the file is password protected or not
            if doc.needs_pass:
                raise ResumeEncryptError(f"System could not open the encrypted and encoded file: {file_path}")
            
            for page in doc:
                text += page.get_text("Text")
        
        # if the text is empty 
        if text.strip() == "":
            raise ResumeTextEmpty("No text is extracted and the output is empty")   
             
        return text # returning the reference where the text is stored      
    except FileNotFoundError as e:
        raise ResumeFileNotFound(f"System could not locate : {file_path}") from e
    except pdf.EmptyFileError as e:
        raise ResumeFileEmpty(f"No Data is found in the file: {file_path}") from e
    except pdf.FileDataError as e:
        raise ResumeCorrupted(f"Not able to read the file : {file_path}") from e
    except Exception as e:
        raise ResumeExtractionError("An unknown error is occured during text extraction") from e
    
def extract_links(text):
    try:
        # check whether the text is a str or not
        if not isinstance(text, str):
            raise InvalidTextInputError("Text is not a String")
        
        # regex patterns for finding the github , email and linkedin from the text
        github_pattern = r'(?i)(?:https?:\/\/)?(?:www\.)?github\.com\/([A-Za-z0-9-]{1,39})\/?'
        linkedin_pattern = r'(?i)(?:https?:\/\/)?(?:www\.)?linkedin\.com\/in\/([A-Za-z0-9-_%]{3,100})\/?'
        email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        
        # finding the links from the text
        github = re.findall(github_pattern, text)
        linkedin = re.findall(linkedin_pattern, text)
        email = re.findall(email_pattern, text)
        
        #for finding the phone numbers
        matches = phonenumbers.PhoneNumberMatcher(text, region= 'In')
        phonenos = []
        for match in matches:
            phoneno = phonenumbers.format_number(match.number, phonenumbers.PhoneNumberFormat.E164)
            phonenos.append(phoneno)
        
        # returning all the links in the format of a object
        return {
            "github": github,
            "linkedin": linkedin,
            "email" : email,
            "phoneno": phonenos
        }
        
    except Exception as e:
        raise LinkExtractionError("An unknow error is occured during the link extraction") from e
    
    
    