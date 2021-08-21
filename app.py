from flask import Flask, render_template,request,redirect,url_for
import os
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = './static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route("/cats")
def index():
    return render_template("cats/index.html")

@app.route("/cats/create",methods=["POST","GET"])
def create():
    if request.method == "POST" : 
        name = request.form['name']
        files = request.files.getlist("files")
        filenames = [] 
        for file in files :
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                filenames.append(filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        print(f"Filename are {','.join(filenames)} ")
        return redirect('/cats')
    else :
        return render_template("cats/create.html")

@app.route('/cats/edit/<int:id>',methods=["POST","GET"])
def edit(id):
    if request.method == "POST":
        print(f"Edit id is {id}")
        return f"Comming with Post Method id is {id}"
    else : 
        print("Comming with Get method")
        return f"Comming with Get Method {id}"



def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

if __name__ == "__main__":
    app.run()