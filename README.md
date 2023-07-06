# How to run?
1) Clone the Github Repository
2) Open Terminal & go to your folder where you have cloned it.
3) Run sudo docker-compose up --build
4) Open one more terminal & run sudo docker ps, here you must see 2 containers running
5) In the mysql container you may need to check for the existence of the table contact. If it is not present then create a table contact.
6) Exit that container & go in flask container & hit the following curl coomand:
     curl -X POST -H "Content-Type: application/json" -d '{"phoneNumber":"<enter a string>","email":"<enter a string>"}' http://localhost:5000/identify

# Features inculcated
1) If the phone number or email is already existing & other entity is non-existent then new contact is created with linkedId equal to parent_id.
2) If the phone number & email is already existing then the contact with phone number changes to seconday & its linkedid is also changed to id of the contact
   having email mentioned, the contacts which were child contacts of the id having phone number also change their linkedId to id of the contact having email mentioned. 
3) If nothing is present then new contact is created.

# Commands
1) To run & build : sudo docker-compose up --build
2) To check for running containers: sudo docker ps
3) To enter in a running container: sudo docker exec -it <container_id> bash (you will get the conatiner id from previous command)
4) For creating contact table 
CREATE TABLE contact (
  id INT AUTO_INCREMENT,
  email VARCHAR(200) NULL,
  phoneNumber VARCHAR(200) NULL,
  linkedId INT NULL,
  linkPrecedence VARCHAR(200) NULL,
  createdAt DATETIME,
  updatedAt DATETIME,
  deletedAt DATETIME NULL,
  PRIMARY KEY (id)
);
