from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask_cors import CORS, cross_origin

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://b5xt55al5mp52ni8:ww84p1dfvw33t2ky@k2fqe1if4c7uowsh.cbetxkdyhwsb.us-east-1.rds.amazonaws.com:3306/akodhyt06164v5xt'
CORS(app, support_credentials=True)

db = SQLAlchemy(app)

if __name__ == "__main__":

    from views import *
    app.run(debug=True)
