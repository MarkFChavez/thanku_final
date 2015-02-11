import os
from datetime import datetime
from flask import Flask, flash, request, redirect, render_template, url_for, session, jsonify, g
from flask.ext.script import Manager
from flask.ext.sqlalchemy import SQLAlchemy
from rauth.service import OAuth2Service
from flask.ext.login import LoginManager
from flask.ext.login import UserMixin, login_required, login_user, logout_user, current_user

basedir = os.path.abspath(os.path.dirname(__file__))
graph_url = "https://graph.facebook.com/"
FB_CLIENT_ID = "770624836357224"
FB_CLIENT_SECRET = "28a5c399b2aeeb8c3b0105ab32b60674"
SECRET_KEY = "sample secret"
SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(basedir, "data.sqlite")
SQLALCHEMY_COMMIT_ON_TEARDOWN = True
DEBUG = True

app = Flask(__name__)
app.config.from_object(__name__)
manager = Manager(app)
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.session_protection = "strong"
login_manager.login_view = "index"
login_manager.init_app(app)

facebook = OAuth2Service(
    name="facebook",
    authorize_url="https://www.facebook.com/dialog/oauth",
    access_token_url=graph_url + "oauth/access_token",
    client_id=app.config["FB_CLIENT_ID"],
    client_secret=app.config["FB_CLIENT_SECRET"],
    base_url=graph_url
)

class User(UserMixin, db.Model):
  __tablename__ = "users"
  id = db.Column(db.Integer, primary_key=True)
  fbid = db.Column(db.String(128))
  image = db.Column(db.String(256))
  first_name = db.Column(db.String(128))
  last_name = db.Column(db.String(128))

  def __repr__(self):
    return "<User %r>" % self.full_name()

  def full_name(self):
    return self.first_name + " " + self.last_name

  def to_json(self):
    json_user = {
      "id": self.id,
      "fbid": self.fbid,
      "image": self.image,
      "first_name": self.first_name,
      "last_name": self.last_name
    }

    return json_user

@app.route("/")
def index():
  return render_template("login.html")

@app.route("/facebook/login")
def login():
  redirect_uri = url_for("authorized", _external=True)
  params = { "redirect_uri": redirect_uri }
  return redirect(facebook.get_authorize_url(**params))

@app.route("/facebook/authorized")
def authorized():
  if not "code" in request.args:
    flash("You did not authorize the request")
    return redirect(url_for("index"))

  redirect_uri = url_for("authorized", _external=True)
  data = dict(code=request.args["code"], redirect_uri=redirect_uri)

  oauth_session = facebook.get_auth_session(data=data)
  me = oauth_session.get("me").json()

  print(me)

  user = User.query.filter_by(fbid=me["id"]).first()

  if user is None:
    user = create_user(me)
    login_user(user)
  else:
    login_user(user)

  return redirect(url_for("dashboard"))

@app.route("/dashboard")
@login_required
def dashboard():
  return render_template("dashboard.html")

@app.route("/logout")
@login_required
def logout():
  logout_user()
  return redirect(url_for("index"))

@login_manager.user_loader
def load_user(user_id):
  return User.query.get(user_id)

def create_user(me):
  image = "https://graph.facebook.com/" + me["id"] + "/picture"
  user = User(first_name=me["first_name"],last_name=me["last_name"],fbid=me["id"],image=image)
  db.session.add(user)
  db.session.commit()

  return user

if __name__ == "__main__":
  manager.run()


