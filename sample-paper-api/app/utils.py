from cleantext import clean

def text_cleanup(text:str):
    cleaned_text = clean(text,
                     fix_unicode=True,  # fix various unicode errors
                     to_ascii=True,     # transliterate to closest ASCII representation
                     lower=True,        # lowercase text
                     no_line_breaks=True,  # remove line breaks
                     no_urls=True,      # replace all URLs with a special token
                     no_emails=True,    # replace all email addresses with a special token
                     no_phone_numbers=True,  # replace all phone numbers with a special token
                     no_numbers=True,   # replace all numbers with a special token
                     no_digits=True,    # replace all digits with a special token
                     no_currency_symbols=True,  # replace all currency symbols with a special token
                     no_punct=True,     # remove punctuations
                     replace_with_url="<URL>",
                     replace_with_email="<EMAIL>",
                     replace_with_phone_number="<PHONE>",
                     replace_with_number="<NUMBER>",
                     replace_with_digit="0",
                     replace_with_currency_symbol="<CUR>",
                     lang="en")         # set to 'en' for English
    return cleaned_text