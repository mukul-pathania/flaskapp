#DBcm is imported to be able to use "with" statement 
#with the database connection and to use the Exceptions defined in it.
from DBcm import *
#app is imported to use app.confing["DB_CONFIG"]
from app import app, login
#This import will let us store and check password hashes.
from werkzeug.security import generate_password_hash, check_password_hash
#
from flask_login import UserMixin
#hashlib is imported to use the avatar service in the Users class.
from hashlib import md5
#Imported to use datetime.utcnow()
from datetime import datetime

@login.user_loader
def load_user(id):
    return get_user(int(id))

def database_interface(_SQL=None, data=None):
    """ The below defined function is work in progress. It is going to 
    be created keeping in mind the heavy usage of the databases in the 
    below code and the redundacy that is created to handle the exceptions
    while using the database.""" 
    #This function executes the sql query that is provided to it and 
    #returns the results to the user if any. This function returns None 
    #if no query is provided to it and prints an message.

    if _SQL is None:
        print("No query provided!")
        return None
    
    else:
        _SQL=str(_SQL)



    try:
        with UseDatabase(app.config["DB_CONFIG"]) as cursor:
            """If data argument is provided then it means that the 
            sql query uses placeholders and those need to be replaced 
            with the data in the data(a tuple) variable"""
            
            #Check if the data variable is passed to function if it is
            #not passed then it will have the default value of None.
            if data:
                cursor.execute(_SQL, data)
            else:
                cursor.execute(_SQL)
           
           
            """The below code is written because whenever cursor.fetchall()
            is called and if it has no result set to fetch from then it 
            raises an error."""
            try:
                return cursor.fetchall()
            except:
                return None
    
    #The following exceptions are defined in the DBcm module and are 
    #reused as is from the book Head First Python(Which taught me Python.)
    except ConnectionError as err:
        print("Is your database switched on? Error: ", str(err))
    except CredentialsError as err:
        print("User-id/Password issues. Error: ", str(err))
    except SQLError as err:
        print("Is your query correct? Error: ", str(err))
    except Exception as err:
        print("Something went wrong: ", str(err)) 

class Users(UserMixin):
    """THIS IS THE MODEL CLASS FOR THE "users" TABLE IN THE DATABASE."""
    def __init__(self, id=None,username=None,rollno=None,email=None, 
            password_hash=None, about_me=None, last_seen=None):
        #The BIF's int() and string() are used to store the variables
        #as I want them to be.

        #Don't touch this until you understand this if-else conditions.
        #It is put here because when a new user fills the registration form
        #a user object is created and value for id is not provided and 
        #the default value None is used which causes an error when it is
        #passed to int() BIF.
        if id:
            self.id=int(id)
        else:
            self.id=id
        self.username=str(username)
        self.rollno=str(rollno)
        self.email=str(email)
        self.password_hash=str(password_hash)
        self.about_me=str(about_me)
        self.last_seen=str(last_seen)

    def __repr__(self):
        return '<Users {}>'.format(self.username)

    def set_password(self,password):
        self.password_hash=generate_password_hash(password)

    def check_password(self,password):
        return check_password_hash(self.password_hash, password)

    def avatar(self,size):
        """This method uses the user's email id to get a profile
        image for him from gravatar. The query arguments d and s define
        what to do when the user is not registered and teh size of the image
        to be returned respectively.
        The size argument will return the image scaled to that size 
        in pixels."""
        digest = md5(self.email.lower().encode("utf-8")).hexdigest()
        return "https://www.gravatar.com/avatar/{}?d=identicon&s={}".format(
                digest, size)


    def follow(self, user):
        """This function allows a user to follow othe users. This function 
        accepts the user object of the user to be followed and then writes
        to the database."""
        if not self.is_following(user):
            #check if the user is not being already followed.
            _SQL = "INSERT INTO followers(follower_id, followed_id)\
                    VALUES (%s,%s)"
            data = (self.id, user.id)
            database_interface(_SQL=_SQL, data=data)

       
    
    def unfollow(self, user):
        """ This function allow users to unfollow anyone whom he is 
        following. This function accepts the user object of the user to be 
        unfollowed and then writes to the database."""
        if self.is_following(user):
            #check if user is being followed.
            _SQL = "DELETE FROM followers WHERE (follower_id=%s AND \
                    followed_id=%s)"
            data =(self.id, user.id)

            database_interface(_SQL=_SQL, data=data)

    def is_following(self, user):
        """This function returns True if the current user follows the 
        given user otherwise False is returned."""

        _SQL="SELECT * FROM followers WHERE (follower_id =%s AND \
                followed_id =%s)"
        data=(self.id, user.id)
        results=database_interface(_SQL=_SQL, data=data)
        if results:
            return True
        return False

    def follower_count(self):
        """This method returns the count of followers of the user."""
        _SQL="SELECT count(*) FROM followers WHERE followed_id=%s"
        data = (self.id,)
        result=database_interface(_SQL=_SQL, data=data)
        return result[0][0]

    def followed_count(self):
        """This method returns the count of the users the user is following."""
        _SQL="SELECT count(*) FROM followers WHERE follower_id=%s"
        data=(self.id,)
        result=database_interface(_SQL=_SQL, data=data)
        return result[0][0]

    def followed_posts(self):
        """This function will return the list of posts(objects of class Posts)
        posted by all the users that this user follows and his own posts arranged according 
        to timestamp of the posts. """
        _SQL="SELECT id, body, timestamp, link, user_id FROM posts, followers\
                WHERE posts.user_id=followers.followed_id AND \
                followers.follower_id=%s order by timestamp  desc"
        data = (self.id,)
        #results is a list of tuples. Tuples contain all the elements
        #extracted from a row.
        results=database_interface(_SQL=_SQL, data=data)
        #The tuples inside the list are also converted to lists.
        results=[list(result) for result in results]
        #posts contain the list of Posts objects to be returned
        posts=list()
        #Binary data is returned from database(bytearray)
        #which is converted to usable form.
        for i in range(len(results)):
            for j in range(len(results[i])):
                if isinstance(results[i][j], bytearray):
                    results[i][j]=results[i][j].decode()
            #After decoding the data is converted to a Posts object and
            #added to the list.
            posts.append(Posts(id=results[i][0],body=results[i][1],
                timestamp=results[i][2], link=results[i][3],
                user_id=results[i][4]))
        #Now add Posts written by the user himself.
        _SQL="SELECT id, body, timestamp, link, user_id from posts WHERE\
                user_id={}".format(self.id)
        results=database_interface(_SQL)
        results=[list(result) for result in results]
        for i in range(len(results)):
            for j in range(len(results[i])):
                if isinstance(results[i][j], bytearray):
                    results[i][j]=results[i][j].decode()
            posts.append(Posts(id=results[i][0],body=results[i][1],
                timestamp=results[i][2], link=results[i][3],
                user_id=results[i][4]))
        #return sorted list according to timestamp of the posts.
        return sorted(posts, key=lambda x: x.timestamp, reverse=True)


        
    def write(self):
        """This function helps to write the newly created users
        into the database after they fill out the registration form."""
        
#        _SQL = "INSERT INTO users (username,rollno,email,password_hash)\
#               VALUES ({},{},{},{})".format(self.username, self.rollno,
#                self.email,self.password_hash)
        
# The above commented out query doesn't work well (unexpectedly).
        _SQL = "INSERT INTO users(username, rollno, email, password_hash)\
                VALUES (%s,%s,%s,%s)"
        data = (self.username, self.rollno, self.email, self.password_hash)
        database_interface(_SQL=_SQL, data=data)
       
    def update(self):
        """This function updates the database with the current information 
        stored in the object. This function is useful whenever a user
        updates any of his information and it is to be updated in the 
        database."""
        _SQL = "UPDATE users SET username=%s, rollno=%s, email=%s, \
                password_hash=%s, about_me=%s, last_seen=%s WHERE id=%s"
        data = (self.username, self.rollno, self.email, self.password_hash,
                self.about_me, self.last_seen, self.id)

        database_interface(_SQL=_SQL, data=data)




class Posts():
    """THIS IS A MODEL CLASS FOR THE "posts" TABLE IN DATABASE."""
    def __init__(self, body, timestamp, link, user_id=None,id=None):
        #This will initialise the posts object.
        if id:
            self.id=int(id)
        else:
            self.id=id
        self.body= str(body)
        self.timestamp=str(timestamp)
        self.link=str(link)
        self.user_id=int(user_id)
        #author will store the Users object of the user who have written
        #the post.
        self.author=get_user(self.user_id)
    
    def write(self, user):
        """This function helps in writing the newly created posts to 
        the database."""

        _SQL = "INSERT INTO posts(body, timestamp, link, user_id) VALUES\
                (%s,%s,%s,%s)"
        data = (self.body, str(datetime.utcnow())[:19], self.link, user.id)
        database_interface(_SQL=_SQL, data=data)

    def update(self):
        """This function updates the database with the current information 
        stored in the object. This is useful whenever a post is edited."""
#[:19] is used in datetime.utcnow() to get the string form of time only till 
#the seconds and not more precise than it.
        _SQL = "UPDATE posts SET body=%s, timestamp=%s, link=%s WHERE id=%s"
        data = (self.body, str(datetime.utcow())[:19], self.link, self.id)
        database_interface(_SQL=_SQL, data=data)

    
    def __repr__(self):
        return "<Posts {}>".format(self.body)


#Note for me.
"""I will be using the function utc_timestamp in the database."""


def get_user(id=None, username=None, rollno=None,
        email=None) -> "Users":

    """THIS FUNCTION IS A HELPER FUNCTION TO LOAD USERS FROM THE DATABASE.
    IT WILL SEARCH THE DATABASE WITH THE GIVEN ARGUMENTS FOR THE USER AND 
    WILL RETURN THE TOPMOST RESULT AS AN OBJECT OF THE users CLASS AS DEFINED
    ABOVE.
    THIS FUNCTION WILL RETURN None IF THE ARGUMENTS PROVIDED ARE NOT PROPER
    OR NO USER WITH THESE CREDENTIALS EXIST IN THE DATABASE.
    I HAVE TRIED MY BEST TO MAKE THIS CODE SELF EXPLANATORY. """
    
    # id the most preferable option to lookup the table as it is the
    #primary key of the table
    # if id is not provided then the other arguments will be 
    #used(arranged according to ease of lookup in the database)
    if id:
        _SQLsub="WHERE id=%s"
        data = (id,)
                 
    elif username:
        _SQLsub="WHERE username=%s"
        data = (username,)
       
    elif rollno:
        _SQLsub="WHERE rollno=%s"
        data = (rollno,)

    elif email:
        _SQLsub="WHERE email=%s"
        data = (email,)

    else:
        #if no arguments are provided then the function return None
        print("Some arguments are required by this \
                function to work properly.")
        return None

    if _SQLsub:
        #Continue only if a part of the SQL query is formed.
        _SQL="SELECT * FROM users {}".format(_SQLsub)
        #users_from_database is the variable that will store results 
        #returned by the function.
        users_from_database=None

    else:
        #I don't know if it should be here but I put it for extra 
        #safety. As the above else statement also returns none 
        # if the  _SQLsub variable is not defined.
        return None

    users_from_database = database_interface(_SQL=_SQL, data=data)    
    # If users with the given info exist then it will be 
    #returned as a list of tuples and I am only intrested 
    #in the topmost result so I retrieve it.
    if users_from_database:
        #As the the database returns binary data(bytearray to be specific)
        #so I would need to covert it to string but as it is stored in a 
        #tuple and the fact that tuples are immutable makes me convert
        #it into list 
        user=list(users_from_database[0])
        for i in range(len(user)):
            #For every object in the list check if they are instances 
            # of type bytearray if yes, then decode them and store
            #back in the list 
            if isinstance(user[i],bytearray):
                user[i] = user[i].decode()
        # If all is fine then return the user object with the details
        #from the list.
        return Users(id=user[0], username=user[1], rollno=user[2],
                     email=user[3], password_hash=user[4],
                     about_me=user[5],last_seen=user[6])
    else:
        #If no users with the given info exist just
        #print the following message and return None.
        #print("No users exist with the given info.")
        return None
      
def get_posts():
    """This function returns the list of all Posts objects from the 
    database arranged according to the timestamp."""
    _SQL="SELECT id, body, timestamp, link, user_id FROM posts\
           ORDER BY timestamp DESC"
    results=database_interface(_SQL)
    #The tuples inside the list are also converted to lists.
    results=[list(result) for result in results]
    #posts contain the list of Posts objects to be returned
    posts=list()
    #Binary data is returned from database(bytearray)
    #which is converted to usable form.
    for i in range(len(results)):
        for j in range(len(results[i])):
            if isinstance(results[i][j], bytearray):
                results[i][j]=results[i][j].decode()
        #After decoding the data is converted to a Posts object and
        #added to the list.
        posts.append(Posts(id=results[i][0],body=results[i][1],
            timestamp=results[i][2], link=results[i][3],
            user_id=results[i][4]))
    return sorted(posts, key=lambda x: x.timestamp, reverse=True)
