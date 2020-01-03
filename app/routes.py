from flask import render_template
from app import app


@app.route("/")
@app.route("/index")
def index ():
    user = {"username":"Mukul"}
    posts = [{"author" : {"username" : "Sunita"},
            "body" : "Beautiful day in Kharghar"} ,
            { "author" : {"username" : "Vishav"} ,
                "body" : "That child was way too cute."}
            ]
    return render_template("index.html",
            title = "Home", 
            user = user,
            posts=posts)
