from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///sharp_class.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(10), nullable=False)  # admin or student

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    video_url = db.Column(db.String(200), nullable=True)
    audio_url = db.Column(db.String(200), nullable=True)

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data['username']
    password = data['password']

    user = User.query.filter_by(username=username).first()
    if user and check_password_hash(user.password, password):
        return jsonify({'role': user.role})
    return jsonify({'error': 'Invalid credentials'}), 401

@app.route('/register', methods=['POST'])
def register():
    data = request.json
    username = data['username']
    password = data['password']
    role = data['role']

    if User.query.filter_by(username=username).first():
        return jsonify({'error': 'User already exists'}), 400

    hashed_password = generate_password_hash(password)
    user = User(username=username, password=hashed_password, role=role)
    db.session.add(user)
    db.session.commit()
    return jsonify({'message': 'User registered successfully'})

@app.route('/posts', methods=['POST', 'GET'])
def posts():
    if request.method == 'POST':
        data = request.json
        post = Post(content=data['content'], video_url=data.get('video_url'), audio_url=data.get('audio_url'))
        db.session.add(post)
        db.session.commit()
        return jsonify({'message': 'Post created successfully'})

    posts = Post.query.all()
    return jsonify([
        {'id': post.id, 'content': post.content, 'video_url': post.video_url, 'audio_url': post.audio_url}
        for post in posts
    ])

@app.route('/comments/<int:post_id>', methods=['POST', 'GET'])
def comments(post_id):
    if request.method == 'POST':
        data = request.json
        comment = Comment(post_id=post_id, content=data['content'])
        db.session.add(comment)
        db.session.commit()
        return jsonify({'message': 'Comment added successfully'})

    comments = Comment.query.filter_by(post_id=post_id).all()
    return jsonify([{'id': c.id, 'content': c.content} for c in comments])

# Create an admin user (if doesn't already exist)
def create_admin():
    if not User.query.filter_by(username='sharp').first():
        hashed_password = generate_password_hash('ssali Ibrahim')
        admin = User(username='sharp', password=hashed_password, role='admin')
        db.session.add(admin)
        db.session.commit()
        print('Admin user created.')
    else:
        print('Admin user already exists.')

@app.before_first_request
def initialize():
    db.create_all()
    create_admin()

if __name__ == '__main__':
    app.run(debug=True)