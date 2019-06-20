from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from app import db, login , app
from flask_login import UserMixin
from hashlib import md5
from time import time
import jwt

followers = db.Table('followers',
    db.Column('follower_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('followed_id', db.Integer, db.ForeignKey('user.id'))
)

class User(UserMixin, db.Model):
    #every time a new thing is added to db (ie. db.Column intialize) we need to 'flask db migrate -m "message"' followed by 'flask db upgrade/downgrade'
    id = db.Column(db.Integer, primary_key=True)
    #db.Column adds a column called id into the User.Model(which is a table-like db), where it defines the data type at Integer; primary_key designates a unique, non-null value for each entry
    username = db.Column(db.String(64), index=True, unique=True)
    #index=True makes the username column indexable for lookup, unique=True means that usernames are non-repeatable/unique
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    posts = db.relationship('Post', backref='author', lazy='dynamic')
    #db.relationship points to the 'Post' class (below)
    #backref creates a way to reference the User in the Post class (my_post.author would refer to a specific user that wrote my_post)
    #lazy defines WHEN sqlalchemy will load this data
    about_me = db.Column(db.String(140))
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    followed = db.relationship(
        'User', secondary=followers,
        primaryjoin=(followers.c.follower_id == id),
        secondaryjoin=(followers.c.followed_id == id),
        backref=db.backref('followers', lazy='dynamic'), lazy='dynamic')

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def avatar(self, size):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest() #gravitar requires lowercase email input, and also md5 in python requires data in bytes, not strings, thus encode utf-8 is used
        return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(
            digest, size)

    def is_following(self, user):
        return self.followed.filter(
            followers.c.followed_id == user.id).count() > 0

    def follow(self, user):
        if not self.is_following(user):
            self.followed.append(user)

    def unfollow(self, user):
        if self.is_following(user):
            self.followed.remove(user)

    #this method is non-trivial; it follows the structure 'Post.query.join(...).filter(...).order_by(...)'
    #Post.query.join(followers, (followers.c.followed_id == Post.user_id))
    #.join links the Post db with the followers db if the condition(followed_id == user_id) is met
    #.filter(followers.c.follower_id == self.id) shrinks the joined db if the condition is true
    #.order_by(Post.timestamp.desc()) orders the filtered db by newest first
    #.union(own) combines the two queries 'followed' and 'own'
    def followed_posts(self):
        followed = Post.query.join(
            followers, (followers.c.followed_id == Post.user_id)).filter(
                followers.c.follower_id == self.id)
        own = Post.query.filter_by(user_id=self.id)
        return followed.union(own).order_by(Post.timestamp.desc())

    def get_reset_password_token(self, expires_in=600):
        return jwt.encode(
            {'reset_password': self.id, 'exp': time() + expires_in},
            app.config['SECRET_KEY'], algorithm='HS256').decode('utf-8')

    @staticmethod
    def verify_reset_password_token(token):
        try:
            id = jwt.decode(token, app.config['SECRET_KEY'],
                            algorithms=['HS256'])['reset_password']
        except:
            return
        return User.query.get(id)

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return '<Post {}>'.format(self.body)

@login.user_loader
def load_user(id):
    return User.query.get(int(id))

