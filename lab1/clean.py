import sys
import re
from unidecode import unidecode 
import string

def clean_text(txt):
	
	s = txt.lower()
	s = re.sub('\n', ' ', s)
	s = unidecode(s)
	s = s.translate(str.maketrans('', '', string.punctuation))
	s = re.sub(' +', ' ', s)
	
	return s
		
def main():
	
	txt = open(sys.argv[1])
	cleaned = clean_text(txt.read())
	open("new_txt.txt", "w").write(cleaned)
	
if __name__ == "__main__":
	main()

