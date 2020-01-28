import re

def terms(line, newfile):
    ignore = ["&#10;", "&lt;", "&gt;", "&amp;", "&apos;", "&quot;"]
    #subbing all of the characters to ignore with spaces
    for char in ignore:
        line = re.sub(char, " ", line)
    #will catch any numbers besides &#10;
    numbers = re.findall("&#(.*);", line)
    #will catch any &#number; characters
    ignore_num = []
    for num in numbers:
        char = "&#" + num + ";"
        ignore_num.append(char)
    #subbing each invalid character with empty space
    for char in ignore:
        line = re.sub(char, " ", line)

    row = re.findall("<row>(.*)</row>", line)
    if row != [] and row != ['']:
        row = str(row[0])
    subject = re.findall("<subj>(.*)</subj>", line)
    body =  re.findall("<body>(.*)</body>", line)

    valid_words_s = []
    if subject != [] and subject != ['']:
        for line in subject:
            #valid_words = []
            line = line.split()
            for word in line:
                new_word = []
                for letter in word:
                    letter = letter.lower()
                    if letter.isalnum():
                        new_word.append(letter)
                    elif letter == "-" or letter == "_":
                        new_word.append(letter)
                    else:
                        new_word.append(" ")
                word = "".join(new_word)
                words = word.split()
                for word in words:
                    if len(word) > 2:
                        valid_words_s.append(word)

    if valid_words_s != []:
        for word in valid_words_s:
            format = "s-" + word + ":" + row + "\n"
            newfile.write(format)

    valid_words_b = []
    if body != [] and body != ['']:
        for line in body:
            #valid_words = []
            line = line.split()
            for word in line:
                new_word = []
                for letter in word:
                    letter = letter.lower()
                    if letter.isalnum():
                        new_word.append(letter)
                    elif letter == "-" or letter == "_":
                        new_word.append(letter)
                    else:
                        new_word.append(" ")
                word = "".join(new_word)
                words = word.split()
                for word in words:
                    if len(word) > 2:
                        valid_words_b.append(word)
    if valid_words_b != []:
        for word in valid_words_b:
            format = "b-" + word + ":" + row + "\n"
            newfile.write(format)

def otherfiles(name):
    #creates the files for emails, dates, and rects
    #open the file
    content = open(name).read()
    
    #EMAILS.txt
    e = open('emails.txt','w')
    #fromTo = {}

    #storing all of the information between tags in respective lists
    froms = re.findall('<from>(.*)</from>', content)
    to = re.findall('<to>(.*)</to>', content)
    row = re.findall('<row>(.*)</row>', content)
    cc = re.findall('<cc>(.*)</cc>', content)
    bcc = re.findall('<bcc>(.*)</bcc>', content)

    for x,y,z,a,b in zip(froms, to, row, cc, bcc):
        e.write('from-'+x.lower()+':'+z+'\n')
        if y != '':
            newL = y.split(',')
            for f in newL:
                e.write('to-'+f.lower()+':'+z+'\n')
        if a != '':
            newA = a.split(',')
            for jk in newA:
                e.write('cc-'+jk+':'+z+'\n')
        if b != '':
            newB = b.split(',')
            for kj in newB:
                e.write('bcc-'+kj+':'+z+'\n')
    e.close()
    
    #DATES.txt
    d = open('dates.txt','w')

    dates = re.findall('<date>(.*)</date>', content)
    for u,i in zip(dates, row):
        d.write(u+':'+i+'\n')
    d.close()
    
    #RECS.txt
    r = open('recs.txt','w')
    emails = re.findall('<mail>(.*)</mail>', content)
    for j,k in zip(emails,row):
        r.write(k+':<mail>'+j+'</mail>'+'\n')
    r.close()

def main():
    name = "1k.xml"
    file = open(name, "r")
    newfileterms = open("terms.txt", "w")
    for line in file:
        terms(line, newfileterms)
    otherfiles(name)
    newfileterms.close()
    file.close()         
if __name__ == "__main__":
    main()