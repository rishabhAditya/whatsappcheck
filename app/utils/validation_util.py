import re


def validate_email(email):
    # Define the regular expression for a valid email address
    email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'

    # Use the re.match() function to check if the email matches the regex
    if re.match(email_regex, email):
        return True
    else:
        return False



