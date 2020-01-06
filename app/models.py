#DBcm is imported to be able to use "with" statement 
#with the database connection and to use the Exceptions defined in it.
from DBcm import *
#app is imported to use app.confing["DB_CONFIG"]
from app import app


class Users():
    def __init__(self, id=None, username=None, rollno=None,
                 email=None, password_hash=None):
        """THIS IS THE MODEL CLASS FOR THE "users" TABLE IN THE DATABASE."""

        #The BIF's int() and string() are used to store the variables
        #as I want them to be.
        self.id=int(id)
        self.username=str(username)
        self.rollno=str(rollno)
        self.email=str(email)
        self.password_hash=str(password_hash)

    def __repr__(self):
        return '<User {}>'.format(self.username)



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
        _SQLsub="WHERE id={}".format(id)
                 
    elif username:
        _SQLsub="WHERE username='{}'".format(username)
       
    elif rollno:
        _SQLsub="WHERE rollno='{}'".format(rollno)

    elif email:
        _SQLsub="WHERE email='{}'".format(email)

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

    try:
        with UseDatabase(app.config["DB_CONFIG"]) as cursor:
            cursor.execute(_SQL)
            users_from_database=cursor.fetchall()
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
                         email=user[3], password_hash=user[4] )
        else:
            #If no users with the given info exist just
            #print the following message and return None.
            print("No users exist with the given info.")
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
      

