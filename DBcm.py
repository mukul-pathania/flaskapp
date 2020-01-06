"""This code is used to handle database connections and the exceptions
that might arise while working with them.
This module is written to work with MySQL databases and will need to change 
if we decide to change the backend database."""

#Does this import need any explanation.
import mysql.connector


class ConnectionError(Exception):
    """This class is created to make it easier for us to know that 
    the database connection could not be created as the database may 
    be turned off. """
    pass

class CredentialsError(Exception):
    """This class is defined to make it easier for us to know that
    there is some issue with our user-id/password provided for the
    database connection."""
    pass

class SQLError(Exception):
    """This Exception is defined to tell us that our query might have
    some errors in it."""
    pass


class UseDatabase():
    """This class is defined to be able to make it easier for us to work 
with the database. This class adheres to the CONTEXT MANAGEMENT PROTOCOL 
and allows us to work with database connections using database connections.

This class automatically commits to the database and closes the connection
as the suite of the "with" statement terminates.
"""
    def __init__(self, config: dict)-> None:
        """config is the dictionary that contains database credentials
        to be used to connect to the database."""
        self.configuration = config

    def __enter__(self)->"cursor":
        try:
            self.connection = mysql.connector.connect(**self.configuration)
            self.cursor = self.connection.cursor()
            return self.cursor
       
        except mysql.connector.errors.InterfaceError as err:
            #This error is raised if the backend database isn't turned on.
            raise ConnectionError(err)
       
        except mysql.connector.errors.ProgrammingError as err:
            #This error is raised if user-id/password provided to connect
            #to the database aren't correct.
            raise CredentialsError(err)

    def __exit__(self, exc_type, exc_value, exc_trace)-> None:
        #Commit the changes to the database.
        self.connection.commit()
        #Close the cursor
        self.cursor.close()
        #Finally close the connection.
        self.connection.close()
        if exc_type is mysql.connector.errors.ProgrammingError:
            #This error will be raised if our query to the database
            #has some issues.
            raise SQLError(exc_value)
        elif exc_type:
            #if the error is of some other type then raise the error again.
            raise exc_type(exc_value)

