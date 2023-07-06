import mysql.connector
from flask import Flask, request, jsonify
from datetime import datetime
from collections import OrderedDict

app = Flask(__name__)

host = 'db1'
port = 3306
user = 'root'
password = 'password'
database = 'Bitespeed'

def get_mysql_connection():
    return mysql.connector.connect(
        host=host,
        port=port,
        user=user,
        password=password,
        database=database
    )

@app.route('/identify', methods=['POST'])
def create_contact():
    email = None
    phoneNumber = None

    data = request.get_json()

    if 'email' in data:
        email = data.get('email')

    if 'phoneNumber' in data:
        phoneNumber = data.get('phoneNumber')

    connection = get_mysql_connection()
    cursor = connection.cursor()

    query_check_alreay_exits = "SELECT COUNT(*) FROM contact WHERE linkPrecedence = %s and phoneNumber = %s"
    cursor.execute(query_check_alreay_exits, ('primary', phoneNumber))
    count = cursor.fetchone()[0]

    query_check_email = "SELECT COUNT(*) FROM contact WHERE linkPrecedence = %s and email = %s"
    cursor.execute(query_check_email, ('primary', email))
    count1 = cursor.fetchone()[0]

    if count > 0 and count1 > 0:
        query_id_phone = "SELECT id FROM contact WHERE linkPrecedence = %s and phoneNumber = %s"
        cursor.execute(query_id_phone, ('primary', phoneNumber))
        changed_id = cursor.fetchone()[0]

        query_id_email = "SELECT id FROM contact WHERE linkPrecedence = %s and email = %s"
        cursor.execute(query_id_email, ('primary', email))
        changing_id = cursor.fetchone()[0]

        query_update = "UPDATE contact SET linkedId = %s, linkPrecedence = %s WHERE id = %s"
        values = (changing_id, 'secondary', changed_id)
        cursor.execute(query_update, values)

        query_change_secondary_linked_to_parent = "UPDATE contact SET linkedId = %s WHERE linkedId = %s"
        values = (changing_id, changed_id)
        cursor.execute(query_change_secondary_linked_to_parent, values)

        connection.commit()

        query_select_primary = "SELECT id, email, phoneNumber FROM contact WHERE linkPrecedence = %s and id = %s"
        values = ('primary', changing_id)
        cursor.execute(query_select_primary, values)


    else:
        query_check_exists = "SELECT COUNT(*) FROM contact WHERE linkPrecedence = %s and (phoneNumber = %s OR email = %s)"
        values = ('primary', phoneNumber, email)
        cursor.execute(query_check_exists, values)
        count = cursor.fetchone()[0]

        if count > 0:
            query_id = "SELECT id FROM contact WHERE linkPrecedence = %s and (phoneNumber = %s OR email = %s)"
            values = ('primary', phoneNumber, email)
            cursor.execute(query_id, values)
            row = cursor.fetchone()
            new_contact = (email, phoneNumber, 'secondary', row[0], datetime.now(), datetime.now())
            query_insert = "INSERT INTO contact (email, phoneNumber, linkPrecedence, linkedId, createdAt, updatedAt) VALUES (%s, %s, %s, %s, %s, %s)"
            cursor.execute(query_insert, new_contact)
            connection.commit()
            query_select_primary = "SELECT id, email, phoneNumber FROM contact WHERE linkPrecedence = %s AND id = %s"
            values = ('primary', row[0])
            cursor.execute(query_select_primary, values)



        else:
	        new_contact = (email, phoneNumber, 'primary', datetime.now(), datetime.now())
	        query_insert_contact = "INSERT INTO contact (email, phoneNumber, linkPrecedence, createdAt, updatedAt) VALUES (%s, %s, %s, %s, %s)"
	        cursor.execute(query_insert_contact, new_contact)
	        changing_id = cursor.lastrowid

	        connection.commit()

	        query_select_primary = "SELECT id, email, phoneNumber FROM contact WHERE linkPrecedence = %s AND id = %s"
	        values = ('primary', changing_id)
	        cursor.execute(query_select_primary, values)

    # print(cursor.lastrowid)
    primary_contact = cursor.fetchone()
    primary_id = primary_contact[0]
    primary_id_email = primary_contact[1]
    primary_id_phoneNumber = primary_contact[2]

    emails = OrderedDict()
    emails[primary_id_email] = None

    phoneNumbers = OrderedDict()
    phoneNumbers[primary_id_phoneNumber] = None

    query_get_secondary_contacts = "SELECT id, email, phoneNumber FROM contact WHERE linkPrecedence = %s AND linkedId = %s"
    cursor.execute(query_get_secondary_contacts, ('secondary', primary_id))
    secondary_contacts = cursor.fetchall()

    secondaryContactIds = []
    for secondary_contact in secondary_contacts:
    	secondaryContactIds.append(secondary_contact[0])
    	emails[secondary_contact[1]] = None
    	phoneNumbers[secondary_contact[2]] = None
    
    final_emails = list(emails.keys())
    final_phoneNumbers = list(phoneNumbers.keys())

    response = {'primaryContactId': primary_id,'emails': final_emails,'phoneNumbers': final_phoneNumbers,'secondaryContactIds': secondaryContactIds}
    cursor.close()
    connection.close()

    return jsonify(response)

if __name__ == '__main__':
    app.run()
