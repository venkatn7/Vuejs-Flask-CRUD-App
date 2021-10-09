from flask import Flask, request, jsonify
from flask_jwt_extended import create_access_token, create_refresh_token, JWTManager, get_jwt_identity, jwt_required
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from datetime import timedelta
import bcrypt

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:admin@localhost/pyapilab'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
ma = Marshmallow(app)



# Setup the Flask-JWT-Extended extension
app.config["JWT_SECRET_KEY"] = "sdjahgkdskg45%$^hghjfh^%&%53dgfdd535GDG5dhd123"
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(seconds=30)
jwt = JWTManager(app)


# user_info table model
class user_info(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), unique=True, nullable=False)

    def __int__(self,
                user_name,
                email,
                password
                ):
        self.username = user_name,
        self.email = email,
        self.password = password

# role table model
class role(db.Model):
    role_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(45), primary_key=True)
    Description = db.Column(db.String(45))
    user_id = db.Column(db.Integer, db.ForeignKey('user_info.id'))
    role = db.relationship('user_info', backref='role')

    def __init__(self,
                 name,
                 ):
        self.name = name


# Schema for user_info model
class UserSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = user_info

    id = ma.auto_field()
    user_name = ma.auto_field()
    email = ma.auto_field()
    password = ma.auto_field()
    role = ma.auto_field()


# Schema for role model
class roleSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = role
        include_fk = True


user_schema = UserSchema()
role_schema = roleSchema()
users_schema = UserSchema(many=True)

@app.route('/')
def hello_world():
    return "Hey There!"

@app.route('/login', methods=['POST'])
def login():
    email = request.json.get('email', None)
    password = request.json.get('password', None)
    try:
        if not email:
            return 'Missing Email!', 400
        if not password:
            return 'Missing Password!', 400

        user = user_info.query.filter_by(email=email).first()
        if not user:
            return 'User not found!', 404
        if bcrypt.checkpw(password.encode('utf-8'), user.password.encode('utf-8')):
            fetch_role = user_info.query.with_entities(role.name).all()
            additional_claims = {"role": fetch_role}
            access_token = create_access_token(identity={"email": email, "additional_claims": additional_claims})
            refresh_token = create_refresh_token(identity={"email": email, "additional_claims": additional_claims})
            return jsonify(access_token=access_token, refresh_token=refresh_token), 200
        else:
            return 'Wrong Password!'
    except AttributeError:
        return 'Provide an Email and Password', 400


# refresh tokens to access this route.
@app.route("/refresh", methods=["POST"])
@jwt_required(refresh=True)
def refresh():
    identity = get_jwt_identity()
    print(identity)
    access_token = create_access_token(identity=identity)
    return jsonify(access_token=access_token)
    print(access_token)


@app.route('/userList', methods=['GET'])
@jwt_required()
def userList():
    all_records = user_info.query.all()
    result = users_schema.dump(all_records)
    return jsonify({'submitted_data': result})

@app.route('/Home', methods=['GET'])
@jwt_required()
def Home():
    current_user = get_jwt_identity()
    for role in current_user['additional_claims']['role']:
        x = role
        if x == ['User']:
            userEmail = current_user['email']
            return jsonify(logged_in_as={'userEmail': userEmail, 'role': x}), 200
        else:
            return 'Insuffecient roles'

if __name__ == '__main__':
    app.run(debug=True)
