from flask import Flask, flash, request, redirect, render_template, url_for
from flask.ext.script import Manager
from rauth.service import OAuth2Service

FB_CLIENT_ID = "770624836357224"
FB_CLIENT_SECRET = "28a5c399b2aeeb8c3b0105ab32b60674"
SECRET_KEY = "sample secret"
DEBUG = True

app = Flask(__name__)
app.config.from_object(__name__)
manager = Manager(app)

graph_url = "https://graph.facebook.com/"

facebook = OAuth2Service(
    name = "facebook",
    authorize_url = "https://www.facebook.com/dialog/oauth",
    client_id = app.config["FB_CLIENT_ID"],
    client_secret = app.config["FB_CLIENT_SECRET"],
    base_url = graph_url
)

@app.route("/")
def index():
  return render_template("login.html")

@app.route("/facebook/login")
def login():
  redirect_uri = url_for("authorized", _external=True)
  params = { "redirect_uri": redirect_uri }
  return redirect(facebook.get_authorize_url(**params))

if __name__ == "__main__":
  manager.run()
