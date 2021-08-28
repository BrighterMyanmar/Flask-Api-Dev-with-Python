from flask import Flask, render_template,request,redirect,url_for,jsonify
import os
from werkzeug.utils import secure_filename
from flask_sqlalchemy import SQLAlchemy, inspect
from datetime import datetime
from flask_bcrypt import Bcrypt

from flask_jwt_extended import create_access_token
from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended import jwt_required
from flask_jwt_extended import JWTManager

UPLOAD_FOLDER = './static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///test.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = "@123!Abc"

app.config["JWT_SECRET_KEY"] = "@123!Abc"  
jwt = JWTManager(app)

bcrypt = Bcrypt(app)
db = SQLAlchemy(app)

class Serializer(object) : 
   def serilize(self):
      return {c: getattr(self,c) for c in inspect(self).attrs.keys()}

   @staticmethod 
   def serialize_list(l):
      return [m.serilize() for m in l]

class User(db.Model) :
    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(30),nullable=False)
    phone = db.Column(db.String(11),nullable=False)
    password = db.Column(db.String(30),nullable=False)
    created = db.Column(db.DateTime,default=datetime.utcnow)

class Category(db.Model,Serializer):
    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(30),nullable=False)
    image = db.Column(db.String(50),nullable=False)
    created = db.Column(db.DateTime,default=datetime.utcnow)

@app.route("/register",methods=["POST"])
def register():
    body = request.get_json()
    name = body['name']
    phone = body['phone']
    password = body['password']
    password = bcrypt.generate_password_hash(password);
    user = User(name=name,phone=phone,password=password)
    try : 
        db.session.add(user)
        db.session.commit()
        return jsonify({"con":True,"msg":"Register Success"})
    except :
        return jsonify({"con":False,"msg":"DB Error"})

@app.route('/login',methods=["POST"])
def login():
    body = request.get_json()
    phone = body["phone"]
    password = body["password"]
    
    user = User.query.filter_by(phone=phone).first()
    con = bcrypt.check_password_hash(user.password, password);
    if con :
       userIdentity = {"name":user.name,"phone":user.phone}
       access_token = create_access_token(identity=userIdentity)
       return jsonify({"con":True,"token":access_token})
    else : 
        return jsonify({"con":False,"msg":"Creditail Error!"})

@app.route("/cats",methods=["GET"])
def catAll():
    cats = Category.query.all()
    return jsonify({"con":True,"categories":Category.serialize_list(cats)})

@app.route("/cats",methods = ["POST"])
def catCreate():
    name = request.form['name']
    file = request.files['image']
    filename = secure_filename(file.filename)
    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

    cat = Category(name=name,image=filename)

    try: 
        db.session.add(cat)
        db.session.commit() 
        return jsonify({"con":True,"msg":"Category Save!"})
    except :
        return jsonify({"con":false,"msg":"Category Save Error!"})

@app.route('/cats/<int:id>',methods=["GET"])
def singleCat(id) :
   cat = Category.query.get(id)
   return jsonify({"con":True,"category":Category.serilize(cat)})

@app.route('/cats/<int:id>',methods=["PATCH"])
def updateCategory(id):
    cat = Category.query.get(id)
    body = request.get_json()
    cat.name = body["name"]
    try: 
        db.session.commit() 
        return jsonify({"con":True,"msg":"Category Updated"})
    except :
         return jsonify({"con":False,"msg":"Category Updated Fail"})

@app.route('/cats/<int:id>',methods=["DELETE"])
@jwt_required()
def deleteCategory(id):
   current_user = get_jwt_identity()
   print(current_user)
   current_user.role == "Owner"
   cat = Category.query.get(id)
   try: 
      db.session.delete(cat)
      db.session.commit() 
      return jsonify({"con":True,"msg":"Category Deleted"})
   except Exception(error):
      print(e)
      return jsonify({"con":False,"msg":"Category Delete Fail"})


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

if __name__ == "__main__":
    app.run()