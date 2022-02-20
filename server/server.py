import concurrent.futures
from twilio.rest import Client
from flask import Flask
import flask
import sqlite3
app = Flask(__name__)
from flask import request
from flask import render_template

import uuid
import qrcode
import os
import shutil
from urllib.parse import urlparse

QR_FOLDER = os.path.join('static', 'qr_codes')
#TODO set this as envar
TWILO_NUMBER = ""
def isSuitAvailible(suitID):
    '''Given the suit id, check whether its availble'''
    pass

@app.route("/")
def index_page():
        return flask.render_template('suit.html')

@app.route("/qr")
def generate_qr():
        '''allow creation of qr  codes'''
        return render_template("createQR.html")

def saveSuit(suit_id, size, gender):
    #TODO implement clean date and checkout date
    connection = sqlite3.connect("SuitDatabase.db")
    cursor = connection.cursor()
    gender = gender.lower()
    if (gender == "male"):
        gender = 1
    else:
        gender = 0 #female

    sql = "INSERT INTO Suits (suit_id, gender, size, isClean, isAvail) VALUES (?,?,?,?,?)"
    data = (suit_id, gender, size, 1, 1)
    cursor.execute(sql, data )
    connection.commit()
    connection.close()


@app.route('/qr_form', methods=['POST'])
def qr_form():
    #TODO handle when null case is done or when size is empty
    #size will be small, medium, large
    size = (request.form['size'])
    gender = request.form['gender']
    suit_id = str(uuid.uuid4())
    isAvail = True
    #suit_type = request.form['suit_type']
    hostname = urlparse(request.base_url).hostname
    qr_url = hostname + ":5000" + "/qr_code/" + suit_id + ".png"
    qr_name = suit_id + ".png"
    qr_code = qrcode.make(qr_url)
    qr_code.save(qr_name)
    #full_filename = os.path.join(QR_FOLDER, qr_name)

    #move the file into static/qr_codes
    shutil.move(qr_name, "static/qr_codes/")
    saveSuit(suit_id, size, gender)
    print(qr_url)
    return render_template('resultQR.html', qr=qr_name)
    # return a response

def removeEnding(suit_id):
    #TODO this probably isn't needed
    return suit_id.replace(".png", "")


def parse_gender(suit_gender):
    if (suit_gender == "1"):
        return "male"
    else:
        return "female"

#when qr code is scanned, the url will be in the form of base_url + uuid
#uuid is id into table to form the data
@app.route("/qr_code/<uuid>")
def readQR(uuid):
    #TODO this should have the .png extension on it, right?
    #use uuid as key in database
    connection = sqlite3.connect("SuitDatabase.db")
    cursor = connection.cursor()
    sql = '''SELECT * FROM Suits WHERE suit_id = (?) '''
    suit_id_internal = str(uuid)
    suit_id = removeEnding(str(uuid))
    data = (suit_id,)
    suit_gender = ""
    suit_size = ""
    suit_type = ""
    isAvail = False
    for row in cursor.execute(sql, data):
        suit_gender = row[1]
        suit_size = row[2]
        suit_avail = row[4]

    suit_gender = parse_gender( str(suit_gender))
    suit_size = str(suit_size)

    connection.commit()
    connection.close()
    return render_template("SuitResult.html", gender=suit_gender, size=suit_size, suit_id = suit_id_internal)

@app.route("/rent_suit", methods=["POST"])
def rent_suit():
    #TODO handle null cases
    if request.method == 'POST':
        telephone_number = "" + "+" + str(request.form['telephone_number'])
        send_reminder(telephone_number)
        return render_template("SuitRented.html")
    #TODO check if suit is actually availible


def send_reminder(telephone_number):
    account_sid = os.environ['TWILIO_ACCOUNT_SID']
    auth_token = os.environ['TWILIO_AUTH_TOKEN']
    telephone_number = ""
    client = Client(account_sid, auth_token)
    message = client.messages.create(body="Thank you for renting out a suit from the Campus Closet. Please return the suit within 2 weeks.", from_=TWILO_NUMBER, to=telephone_number)

    print(message.sid)


if __name__ == '__main__':
   app.run()
