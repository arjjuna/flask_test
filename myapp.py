import os
import time

from flask_script import Manager, Shell
from flask_migrate import Migrate, MigrateCommand
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate, MigrateCommand
from flask_login import LoginManager, UserMixin, AnonymousUserMixin, \
	login_user, logout_user, current_user, login_required	
from flask_bootstrap import Bootstrap

from flask import Flask, request, \
	render_template, redirect, url_for, jsonify

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import Required, Length


basedir = os.path.abspath(os.path.dirname(__file__))

bootstrap = Bootstrap()
db = SQLAlchemy()
login_manager = LoginManager()


#Utility functions
def timestamp():
	return int(time.time())



class User(UserMixin, db.Model):
	__tablename__ = "users"
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(64))
	password = db.Column(db.String(64), default="123")
	
	messages = db.relationship('Message', lazy='dynamic', backref='user')
	
	online = db.Column(db.Boolean, default=False)
	
	def verify_password(self, password):
		return (password == self.password)
		
	@staticmethod
	def list_online():
		return User.query.filter_by(online=True).all()
		
	def to_dict(self):
		return {
			'id': self.id,
			'name': self.name,
			'online': self.online,
			'_links': {}
		}
		
class Message(db.Model):
	__messages__ = "messages"
	id = db.Column(db.Integer, primary_key=True)
	text = db.Column(db.String(100))
	timestamp = db.Column(db.Integer, default=timestamp)
	user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
	
	@staticmethod
	def list_messages():
		return Message.query.all()
	
	def to_dict(self):
		return {
			'id': self.id,
			'timestamp': self.timestamp,
			'text': self.text,
			'user.id': self.user_id,
			'_links': {}
		}
		
class AnonymousUser(AnonymousUserMixin):
	name = "No body"

login_manager.anonymous_user = AnonymousUser

def create_app(debug=False):
	app = Flask(__name__)
	
	app.config['DEBUG'] = debug
	app.config['SECRET_KEY'] = "i have no secrets"
	
	app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
	app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'db.sqlite')
	
	db.init_app(app)
	bootstrap.init_app(app)
	login_manager.init_app(app)
	
	return app
	
app = create_app(debug = True)

#These extensions are not needed if you want to create an app manualy
manager = Manager(app)
migrate = Migrate(app, db)
manager.add_command('db', MigrateCommand)

def make_shell_context():
	return dict(app=app, db=db, User=User)

manager.add_command("shell", Shell(make_context=make_shell_context))

#User loader view for flask-login_manager
@login_manager.user_loader
def load_user(user_id):
	return User.query.get(int(user_id))

@app.route('/')
def index():
    return 'Wech, World!'

class LoginForm(FlaskForm):
	name = StringField('Name')
	password = PasswordField('Password')
	submit = SubmitField('Login')

@app.route('/login', methods=['GET', 'POST'])
def login():
	form = LoginForm()
	if form.validate_on_submit():
		user = User.query.filter_by(name = form.name.data).first()
		if user is not None and user.verify_password(form.password.data):
			login_user(user)
			user.online = True
			db.session.commit()
			return redirect(url_for('who_logged_in'))
		return "login unsuccessfull"
	return render_template('login.html', form=form)
	
@app.route('/logout')
@login_required
def logout():
	current_user.online = False
	db.session.commit()
	logout_user()
	return redirect(url_for('index'))
	
@app.route('/whosin')
def who_logged_in():
	return "The user logged in is: " + current_user.name

@app.route('/whosonline')
def who_is_online():
	users = User.list_online()
	return render_template('whosonline.html', users=users)
	
class MessageForm(FlaskForm):
	text = StringField('', validators=[Length(1, 100)])
	submit = SubmitField('Envoyer')
	
@app.route('/chat', methods=['GET', 'POST'])
@login_required
def chat():
	form = MessageForm()
	users = User.list_online()
	messages = Message.list_messages()
	if form.validate_on_submit():
		m = Message(text=form.text.data, user=current_user)
		db.session.add(m)
		db.session.commit()
		return redirect('chat')
	return render_template('chat.html', form=form, users=users, messages=messages)
	
@app.route('/api/users')
def api_users():
	#Getting a clients JSON from the api
	users = User.query.all()
	return jsonify({'users': [u.to_dict() for u in users]})		
	
@app.route('/api/online_users')
def api_online_users():
	#Getting a clients JSON from the api
	users = User.query.filter_by(online=True).all()
	return jsonify({'onilne_users': [u.to_dict() for u in users]})	
	
@app.route('/api/users/<int:id>')
def api_user(id):
	#Getting a clients JSON from the api
	user = User.query.get(id)
	return jsonify(user.to_dict())	
	
@app.route('/api/messages')
def api_messages():
	#Getting a clients JSON from the api
	messages = Message.query.all()
	return jsonify({'Messages': [m.to_dict() for m in messages]})	
	
@app.route('/api/messages/<int:id>')
def api_message(id):
	#Getting a clients JSON from the api
	message = Message.query.get(id)
	return jsonify(message.to_dict())	
	
@app.route('/get/online_users')
def get_online_users():
	return render_template('online_users.html')
	
if __name__ == '__main__':
    manager.run()