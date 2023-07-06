from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy import create_engine, text
from orderedset import OrderedSet
from flask import Flask, jsonify, request
from sqlalchemy.orm import sessionmaker
import os


app = Flask(__name__)
# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:password@db:3306/Bitespeed'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:password@db1:1234/Bitespeed'
# if 'DOCKER' in os.environ:
#     app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:password@db:1234/Bitespeed'
# else:
#     app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:password@localhost:3306/Bitespeed'
db = SQLAlchemy(app)
# engine = create_engine('mysql+pymysql://root:password@db:3306/Bitespeed')

class Contact(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	email = db.Column(db.String(200), nullable=True)
	phoneNumber = db.Column(db.String(200), nullable=True)
	linkedId = db.Column(db.Integer, nullable=True)
	linkPrecedence = db.Column(db.String(200), nullable=True)
	createdAt = db.Column(db.DateTime)
	updatedAt = db.Column(db.DateTime)
	deletedAt = db.Column(db.DateTime, nullable=True)


with app.app_context():
    db.create_all()

@app.route('/identify', methods=['POST'])
def create_contact():
    
   ##handle the case where email & phone number both match

	Session = sessionmaker(bind=db.engine)
	session = Session()

	email = None
	phoneNumber = None

	data = request.get_json()
	# print(data)
	if 'email' in data:
		email = data.get('email')

	if 'phoneNumber' in data:
		phoneNumber = data.get('phoneNumber')

	# print(email, ' ', phoneNumber)


	query_check_alreay_exits = text("SELECT COUNT(*) FROM contact WHERE linkPrecedence = :precedence and phoneNumber = :phone")
	result = session.execute(query_check_alreay_exits, {"phone":phoneNumber, "precedence":'primary'})
	count = result.scalar()

	query= text("SELECT COUNT(*) FROM contact WHERE linkPrecedence = :precedence and email = :email")
	result1= session.execute(query, {"email":email, "precedence":'primary'})
	count1 = result1.scalar()
	result_primary_id_query = None

	# print(count,' ', count1)


	if count>0 and count1>0:
		# return 'user already exists'
		# print('user exists')

		query= text("SELECT id FROM contact WHERE linkPrecedence = :precedence and email = :email")
		result1= db.session.execute(query, {"email":email, "precedence":'primary'})

		temp_query = text("Select id from contact where linkPrecedence=:precedence and phoneNumber=:phone")
		temp_result = db.session.execute(temp_query, {"precedence":'primary', "phone":phoneNumber})

		# print(temp_result.fetchone()[0], ' ', result1.fetchone()[0])
		changed_id = temp_result.fetchone()[0]
		changing_id = result1.fetchone()[0]

		print(changed_id, ' ', changing_id)

		# temp_temp_query = text("Select email, phoneNumber from contact where id = :id")
		# temp_temp_query_result = engine.execute(temp_temp_query, id = changed_id)

		# # print(temp_temp_query_result.fetchall())

		query2 = text("UPDATE contact SET linkedId = :linkedId, linkPrecedence =:secondPrecedence WHERE id = :id")
		result2= db.session.execute(query2, {"linkedId":changing_id, "id":changed_id, "secondPrecedence":'secondary'}) 

		query_change_secondary_linked_to_parent = text("UPDATE contact SET linkedId = :linkedId where linkedId = :id")
		query_change_secondary_linked_to_parent_result = db.session.execute(query_change_secondary_linked_to_parent, {"linkedId":changing_id, "id":changed_id})

		# print('#######  ', query_change_secondary_linked_to_parent_result)

		
		# print(result_primary_id_query.fetchall())
		# db.session.commit()

		primary_id_query = text('Select id, email, phoneNumber from contact where linkPrecedence = :precedence and id=:id')
		result_primary_id_query = db.session.execute(primary_id_query, {"id":changing_id,  "precedence":'primary'})

		# print(query_change_secondary_linked_to_parent_result.fetchall())

		# print(result1.fetchone(), ' ', result2.fetchone())
		# return 'user already exists'

	else:
		query = text("SELECT COUNT(*) FROM contact WHERE linkPrecedence = :precedence and (phoneNumber = :phone OR email = :email)")
		result = db.session.execute(query, {"phone":phoneNumber, "email":email, "precedence":'primary'})
		# print(result)


		count = result.scalar()

		if count>0:
			query_id = text("SELECT id FROM contact WHERE linkPrecedence = :precedence and (phoneNumber = :phone OR email = :email)")
			result_id = db.session.execute(query_id, {"phone":phoneNumber, "email":email, "precedence":'primary'})
			row = result_id.fetchone()
			new_contact = Contact(
		        email=email,
		        phoneNumber=phoneNumber,
		        linkPrecedence='secondary',
		        linkedId = row[0],
		        createdAt=datetime.now(),
		        updatedAt=datetime.now()
		    )
			db.session.add(new_contact)

		else:
			new_contact = Contact(
		        email=email,
		        phoneNumber=phoneNumber,
		        linkPrecedence='primary',
		        createdAt=datetime.now(),
		        updatedAt=datetime.now()
		    )
			db.session.add(new_contact)

		db.session.commit()
		primary_id_query = text('Select id, email, phoneNumber from contact where linkPrecedence = :precedence and (phoneNumber = :phone or email = :email)')
		result_primary_id_query = db.session.execute(primary_id_query, {"phone":phoneNumber, "email":email, "precedence":'primary'})
		# db.session.commit()
		# print(result_primary_id_query.fetchall())



	# print(result_primary_id_query)
	# print(type(result_primary_id_query.fetchall()[0]))

	db.session.commit()

	primary_id_rows = result_primary_id_query.fetchone()
	print(primary_id_rows)

	primary_id = primary_id_rows[0]
	primary_id_email  = primary_id_rows[1]
	primary_id_phoneNumber = primary_id_rows[2]

	##fill email in unordered set 
	emails = OrderedSet()
	emails.add(primary_id_email)

	phoneNumbers = OrderedSet()
	phoneNumbers.add(primary_id_phoneNumber)



	# print(primary_id, ' ', primary_id_email, ' ', primary_id_phoneNumber, ' ', type(primary_id))

	secondary_id_query = text('Select id, email, phoneNumber from contact where linkPrecedence = :precedence and linkedId=:id')
	result_secondary_id_query = db.session.execute(secondary_id_query, {"id":primary_id, "phone": phoneNumber, "email":email, "precedence":'secondary'})
	# print(type(result_primary_id_query.fetchall()[0]))
	secondary_id_rows = result_secondary_id_query.fetchall()

	secondaryContactIds = []


	for i in secondary_id_rows:
		secondaryContactIds.append(i[0])
		emails.add(i[1])
		phoneNumbers.add(i[2])

	# print(emails)

	final_emails = []
	final_phoneNumbers = []

	for i in emails:
		final_emails.append(i)

	for i in phoneNumbers:
		final_phoneNumbers.append(i)


	response = {}
	response['primaryContatctId']=primary_id
	response['emails'] = final_emails
	response['phoneNumbers'] = final_phoneNumbers
	response['secondaryContactIds'] = secondaryContactIds

	final_response = {'contact': response}

	# print(final_response)

	return jsonify(final_response)


if __name__ == '__main__':
    app.run()

