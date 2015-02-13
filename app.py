import os
from datetime import datetime
from flask import Flask, flash, request, redirect, render_template, url_for, session, jsonify, g
from flask.ext.script import Manager
from flask.ext.sqlalchemy import SQLAlchemy
from rauth.service import OAuth2Service
from flask.ext.login import LoginManager
from flask.ext.login import UserMixin, login_required, login_user, logout_user, current_user
from flask.ext.cors import CORS

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
cors = CORS(app)
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

class Vote(db.Model):
  __tablename__ = "votes"
  id = db.Column(db.Integer, primary_key=True)
  user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
  recipient_id = db.Column(db.Integer, db.ForeignKey("users.id"))
  timestamp = db.Column(db.DateTime, default=datetime.utcnow)
  reason = db.Column(db.String(255))
  point = db.Column(db.Integer)

  def __repr__(self):
    return "<Vote %r>" % self.reason

  def to_json(self):
    json_vote = {
      "user": User.query.get(self.user_id).to_json(),
      "recipient": User.query.get(self.recipient_id).to_json(),
      "message": self.reason,
      "timestamp": self.timestamp,
      "point": self.point
    }

    return json_vote

class User(UserMixin, db.Model):
  __tablename__ = "users"
  id = db.Column(db.Integer, primary_key=True)
  fbid = db.Column(db.String(128))
  image = db.Column(db.String(256))
  first_name = db.Column(db.String(128))
  last_name = db.Column(db.String(128))

  thanku_recipients = db.relationship("Vote", foreign_keys=[Vote.user_id], backref = db.backref("user", lazy="joined"), lazy="dynamic", cascade="all, delete-orphan")

  thanku_sources = db.relationship("Vote", foreign_keys=[Vote.recipient_id], backref = db.backref("recipient", lazy="joined"), lazy="dynamic", cascade="all, delete-orphan")

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
      "last_name": self.last_name,
      "points": self.total_points()
    }

    return json_user

  def give_credit_to(self, user, point, reason):
    # check if the last credit is given on the same day
    # if same day, do not allow it
    c = Vote(user=self, recipient=user, point=point, reason=reason)
    db.session.add(c)
    db.session.commit()

  def has_given_credit_to(self, user):
    return self.thanku_recipients.filter_by(recipient_id=user.id).first() is not None

  def total_points(self):
    new_array = []
    votes = Vote.query.filter_by(recipient_id=self.id)

    for i in votes:
      new_array.append(i.point)

    return sum(new_array)

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
  users = User.query.all()
  return render_template("dashboard.html", users=users)

@app.route("/api/v1.0/news-feed")
@login_required
def news_feed():
  votes = Vote.query.all()
  return jsonify({ "status": "ok", "votes": [vote.to_json() for vote in votes] })

@app.route("/api/v1.0/top")
def get_top():
  users = User.query.all()
  points = []

  for user in users:
    points.append( (user, user.total_points) )

  return jsonify({ "user": [point[0].to_json() for point in points] })

@app.route("/logout")
@login_required
def logout():
  user = current_user
  user.authenticated = False
  db.session.add(user)
  db.session.commit()

  logout_user()

  return redirect(url_for("index"))

@app.route("/api/v1.0/users")
def users():
  users = User.query.filter(User.id != current_user.id)
  return jsonify({ "users": [user.to_json() for user in users]})

@app.route("/api/v1.0/thank/<int:user_id>", methods=["POST"])
def thank_user(user_id):
  user = current_user

  recipient = User.query.get(user_id)
  point = request.json["point"]
  allowed_to_thank = True

  votes =  Vote.query.filter_by(user_id = user.id, recipient_id = recipient.id, point = point)

  for vote in votes:
    if vote.timestamp.date() == datetime.today().date():
      allowed_to_thank = False
      break

  if request.json.has_key("reason"):
    reason = request.json["reason"]
  else:
    reason = ""

  message = "You gave %d thank(s) to %s. Go get a beer!" % (int(point), recipient.full_name())

  if allowed_to_thank == True:
    user.give_credit_to(recipient, int(request.json["point"]), reason)
    return jsonify({ "status": "ok", "user": user.to_json(), "recipient": recipient.to_json(), "message": message })
  else:
    return jsonify({ "status": "error", "user": user.to_json(), "recipient": recipient.to_json(), "message": "You are not allowed to give 2 points for today" })


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


