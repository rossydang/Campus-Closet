#lets play around with some databases
import sqlite3


connection = sqlite3.connect("SuitDatabase.db")
cursor = connection.cursor()

def run():
    cursor.execute('''CREATE TABLE Suits
               (suit_id text ,
               gender boolean ,
               size text ,
               isClean boolean ,
               isAvail boolean  )''')


if __name__ == '__main__':
   run()