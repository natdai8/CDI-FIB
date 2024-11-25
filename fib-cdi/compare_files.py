import sys

############
### MAIN ###
############

def main(file1, file2):
   with open(file1, 'r', encoding='utf-8') as f1, open(file2, 'r', encoding='utf-8') as f2:
        content1 = f1.read()
        content2 = f2.read()

        if content1 == content2:
            print("The files are identical.")
        else:
            print("The files are different.")

if __name__ == "__main__":
    file1 = sys.argv[1]
    file2 = sys.argv[2]
    main(file1, file2)