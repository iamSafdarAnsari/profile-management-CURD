from flask import Flask, request, jsonify
from flask_bcrypt import Bcrypt
from flask_cors import CORS
import jwt, datetime
from pymongo import MongoClient
import config

app = Flask(__name__, static_folder="../frontend", static_url_path="/")
CORS(app)
app.config['SECRET_KEY'] = config.SECRET_KEY

# MongoDB Atlas connection
client = MongoClient(config.MONGO_URI)
db = client[config.DB_NAME]
users = db["users"]

bcrypt = Bcrypt(app)

@app.route('/')
def index():
    # serve frontend signup page by default
    return app.send_static_file('signup.html')

# ---------------- SIGNUP ----------------
@app.route('/api/signup', methods=['POST'])
def signup():
    data = request.json or {}
    required = ['fullname','email','password']
    for r in required:
        if not data.get(r):
            return jsonify({'error': f'Missing field: {r}'}), 400

    if users.find_one({'email': data['email']}):
        return jsonify({'error': 'Email already registered'}), 400

    hashed_pw = bcrypt.generate_password_hash(data['password']).decode('utf-8')
    user = {
        'fullname': data['fullname'],
        'email': data['email'],
        'password': hashed_pw,
        'phone': data.get('phone', ''),
        'dob': data.get('dob', ''),
        'age': data.get('age', '')
    }
    users.insert_one(user)
    return jsonify({'message': 'User registered successfully'})

# ---------------- LOGIN ----------------
@app.route('/api/login', methods=['POST'])
def login():
    data = request.json or {}
    if not data.get('email') or not data.get('password'):
        return jsonify({'error': 'Email and password required'}), 400
    user = users.find_one({'email': data['email']})
    if user and bcrypt.check_password_hash(user['password'], data['password']):
        token = jwt.encode({
            'email': user['email'],
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=8)
        }, app.config['SECRET_KEY'], algorithm='HS256')
        # pyjwt returns str in newer versions, ensure it's serializable
        if isinstance(token, bytes): token = token.decode('utf-8')
        return jsonify({'token': token})
    return jsonify({'error': 'Invalid credentials'}), 401

# ---------------- GET PROFILE ----------------
@app.route('/api/profile', methods=['GET'])
def get_profile():
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({'error': 'Missing token'}), 401
    try:
        decoded = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        user = users.find_one({'email': decoded['email']}, {'password': 0})
        if not user:
            return jsonify({'error': 'User not found'}), 404
        # convert ObjectId to string and ensure JSON serializable
        user['_id'] = str(user.get('_id'))
        return jsonify(user)
    except jwt.ExpiredSignatureError:
        return jsonify({'error': 'Token expired'}), 401
    except Exception as e:
        return jsonify({'error': 'Invalid token'}), 401

# ---------------- UPDATE PROFILE ----------------
@app.route('/api/profile', methods=['PUT'])
def update_profile():
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({'error': 'Missing token'}), 401
    try:
        decoded = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        data = request.json or {}
        allowed = {'fullname','phone','dob','age'}
        update = {k: v for k, v in data.items() if k in allowed}
        if not update:
            return jsonify({'error': 'No valid fields to update'}), 400
        users.update_one({'email': decoded['email']}, {'$set': update})
        return jsonify({'message': 'Profile updated successfully'})
    except jwt.ExpiredSignatureError:
        return jsonify({'error': 'Token expired'}), 401
    except Exception as e:
        return jsonify({'error': 'Invalid token'}), 401

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
