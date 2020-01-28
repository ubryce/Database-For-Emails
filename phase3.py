from bsddb3 import db
import re 
import datetime

cursor1 = None
cursor2 = None
cursor3 = None
cursor4 = None
database1 = None
database2 = None
database3 = None
database4 = None
mode = "b"  #defualt mode

def create_database():
    global cursor1, cursor2, cursor3, cursor4, database1, database2, database3, database4
    database1 = db.DB()
    database2 = db.DB()
    database3 = db.DB()
    database4 = db.DB()
    database1.open("re.idx", None, db.DB_HASH, db.DB_CREATE)
    database2.open("te.idx", None, db.DB_BTREE, db.DB_CREATE)
    database3.open("em.idx", None, db.DB_BTREE, db.DB_CREATE)
    database4.open("da.idx", None, db.DB_BTREE, db.DB_CREATE)

    cursor1 = database1.cursor()
    cursor2 = database2.cursor()
    cursor3 = database3.cursor()
    cursor4 = database4.cursor()

def user_input():
    global mode
    #gets the user command either query or modechange

    command = input("Enter query here or enter QUIT to exit: ").lower()
    if command == "quit":
        quit()
    else:
        query(command)

def query(query):
    global mode
    #gets the query of the user
    query = re.sub(' +', ' ', query) #maximum of once space between words
    query = re.sub(r'\s([:<=>])', r'\1', query) #removes spaces before character
    query = re.sub(r'([:<=>])\s', r'\1', query) #removes spaces after characters
    queries = query.split() #list of the queries
    characters = ["<=", ">="]
    characters2 = ["<", ">", ":", "="]

    query_char = []
    queries_list = []
    for q in queries:
        found = False
        for char in characters:
            if char in q:
                found = True
                x = q.split(char)          
                query_char.append(char)
                queries_list.append(x)
        if found == False:
            for char in characters2:
                if char in q:
                    found = True
                    query = []
                    x =q.split(char)          
                    query_char.append(char)
                    queries_list.append(x)
        if found == False:
            query_char.append("")
            queries_list.append(q.split())

    if len(queries_list) != len(query_char):
        print("Invalid Query")
        user_input()
        
    rows = {}
    query_count = 0 #counts how many queries there are which will be used later to access the dictionary
    valid = False
    for x in range(len(queries_list)):
        query = queries_list[x]
        char = query_char[x]
        if len(query) == 2:
            keyword = query[0]
            if keyword == "subj" or keyword == "subject" or keyword == "body":
                valid_char = [":"]
                if char in valid_char:
                    query_count += 1
                    valid = True
                    sub_body(rows, query, char)   
            elif keyword == "date":
                valid_char = ["<=", ">=", ":", "<", ">"]
                if char in valid_char:
                    query_count += 1
                    valid = True
                    date(rows, query, char)   
            elif keyword == "bcc" or keyword == "cc" or keyword == "from" or keyword == "to":
                valid_char = [":"]
                if char in valid_char:
                    query_count += 1
                    valid = True
                    emails(rows, query, char) 
            elif keyword == "output":
                valid_char = ["="]
                if char in valid_char:
                    valid = True
                    output(query)
        elif len(query) == 1:
            if char == "":
                query_count += 1
                valid = True
                sub_body(rows, query, char)
    if valid == False:
        print("Invalid Query")
        user_input()
    else:
        if query_count != 0:
            print_output(rows, query_count)
        else:
            user_input()

def sub_body(rows, query, char):
    global cursor2, database2
    #this function iterates over terms.txt and increments value in dictionary for each row_id found
    queries = []    #list of queries
    if len(query) == 2:
        keyword = query[0]
        raw_query = query[1]   #what user is looking for
        if keyword == "subj" or keyword == "subject":
            query_term = "s-" + raw_query
            queries.append(query_term)
        else:
            query_term = "b-" + raw_query
            queries.append(query_term)
    if len(query) == 1:
        raw_query = query[0]   #what user is looking for
        query_term = "s-" + raw_query
        queries.append(query_term)
        query_term = "b-" + raw_query
        queries.append(query_term)
    #iterate throught the database
    current = cursor2.first()
    while current:
        raw_key = current[0]    #key from the k, v pair
        key = raw_key.decode() #turning into string
        #find queries that partially match the target query
        for query_term in queries:
            if query_term.endswith("%"):
                new_query_term = query_term[:-1] #removing % from string
                if key.startswith(new_query_term) or key == new_query_term:
                    row_id = current[1] #value from the k,v pair
                    #adds or increments the found row_id in the dictionary
                    if row_id not in rows:
                        rows[row_id] = 1 
                    else:
                        rows[row_id] += 1
            #find queries that are exactly like the query
            else:
                if key == query_term:
                    row_id = current[1] #value from the k,v pair
                    #adds or increments the found row_id in the dictionary
                    if row_id not in rows:
                        rows[row_id] = 1 
                    else:
                        rows[row_id] += 1
        current = cursor2.next()

def emails(rows,query,char):
    global cursor3, database3
    #this function iterates over emails.txt and increments value in dictionary for each row_id found
    
    keyword = query[0]
    query_term = query[1]   #what user is looking for
    query_term = keyword + "-" + query_term
    #iterate throught the database
    current = cursor3.first()
    while current:
        raw_key = current[0]    #key from the k, v pair
        key = raw_key.decode() #turning into string
        #find queries that are exactly like the query
        if key == query_term:
            row_id = current[1] #value from the k,v pair
            #adds or increments the found row_id in the dictionary
            if row_id not in rows:
                rows[row_id] = 1 
            else:
                rows[row_id] += 1
        current = cursor3.next()

def date(rows, query, char):
    global cursor4, database4
    query_term = query[1]
    query_term = datetime.datetime.strptime(query_term,'%Y/%m/%d').date()
    current = cursor4.first()
    while current:
        raw_key = current[0]    #key from the k, v pair
        key = raw_key.decode() #turning into string
        key = datetime.datetime.strptime(key,'%Y/%m/%d').date()
        if(char == ':'):
            #find queries that partially match the target query
            if key == query_term:
                row_id = current[1] #value from the k,v pair
                #adds or increments the found row_id in the dictionary
                if row_id not in rows:
                    rows[row_id] = 1 
                else:
                    rows[row_id] += 1
        elif(char == '<'):
            if key < query_term:
                row_id = current[1] #value from the k,v pair
                #adds or increments the found row_id in the dictionary
                if row_id not in rows:
                    rows[row_id] = 1 
                else:
                    rows[row_id] += 1
        elif(char == '<='):
            if key <= query_term:
                row_id = current[1] #value from the k,v pair
                #adds or increments the found row_id in the dictionary
                if row_id not in rows:
                    rows[row_id] = 1 
                else:
                    rows[row_id] += 1
        elif(char == '>'):
            if key > query_term:
                row_id = current[1] #value from the k,v pair
                #adds or increments the found row_id in the dictionary
                if row_id not in rows:
                    rows[row_id] = 1 
                else:
                    rows[row_id] += 1
        elif(char == '>='):
            if key >= query_term:
                row_id = current[1] #value from the k,v pair
                #adds or increments the found row_id in the dictionary
                if row_id not in rows:
                    rows[row_id] = 1 
                else:
                    rows[row_id] += 1
        current = cursor4.next()

def print_output(rows, query_count):
    global cursor1, database1
    notfound = True
    if len(rows) != 0:
        for k, v in rows.items():
            if v >= query_count:
                if mode == "b":
                    current = cursor1.first()
                    while current:
                        row_id = current[0]
                        record = current[1].decode()
                        if row_id == k:
                            notfound = False
                            subj_record = re.findall("<subj>(.*)</subj>", record)
                            for subj in subj_record:
                                print(k.decode() + ": " + subj)
                        current = cursor1.next()
                else:
                    current = cursor1.first()
                    while current:
                        row_id = current[0]
                        record = current[1].decode()
                        if row_id == k:
                            notfound = False
                            print(k.decode() + ": " + record + "\n")
                        current = cursor1.next()
    if notfound == True:
        print("No Matches")
    user_input()

def output(query):
    global mode
    if query[1] == "brief":
        mode = "b"
        print("\nOutput changed to brief\n")
    elif query[1] == "full":
        mode = "f"
        print("\nOutput changed to full\n")
    else:
        print("Invalid Query")
        user_input()

def main():
    global cursor1, cursor2, cursor3, cursor4
    create_database()
    user_input()

    database1.close()
    cursor1.close
    database2.close()
    cursor2.close
    database3.close()
    cursor3.close
    database4.close()
    cursor4.close
if __name__ == "__main__":
    main()