import os
import sys
import numpy
import threading
from flask import Flask, jsonify, request, json
import swiftclient
from sklearn.ensemble import RandomForestClassifier
from sklearn.externals import joblib
import requests
import dateutil.parser


from flask_cors import CORS, cross_origin
app = Flask(__name__)
app.config['PROPAGATE_EXCEPTIONS'] = True
CORS(app)

conn = swiftclient.Connection(key="""ApX1Y]C*#tvNn95j""",authurl='https://identity.open.softlayer.com/v3',auth_version='3',
os_options={"project_id": 'c103edd6ab074e8f967770017c08c779',"user_id": '70b92ab4ed014fe0b3564f31a53b6522',"region_name": 'dallas'})
obj_tuple = conn.get_object("Analytics", 'movie_c.gz')

with open('movie_c.gz', 'w') as dl_model:
    dl_model.write(obj_tuple[1])

movie = joblib.load('movie_c.gz')

obj_tuple = conn.get_object("Analytics", 'movie_d.gz')

with open('movie_d.gz', 'w') as dl_model:
    dl_model.write(obj_tuple[1])

d = joblib.load('movie_d.gz')



@app.route('/')
def notice():
	return "This is a webapp"

@app.route('/predict', methods=['GET', 'POST'])
def parse_request():
	try:
		global mpredict
		mpredict = []

		inpredict = [int(d["GENDER"].transform([request.args.get('GENDER')])[0]),int(request.args.get('SENIORCITIZEN')),int(request.args.get('DEPENDENTS')),int(request.args.get('TENURE')),int(request.args.get('PAPERLESSBILLING')),int(d["PAYMENTMETHOD"].transform([request.args.get('PAYMENTMETHOD')])[0]),request.args.get('MONTHLYCHARGES')]
		inpredict = numpy.array(inpredict).reshape(1, (len(inpredict)))	
		
		mtitle = d["title"].inverse_transform(int(movie.predict(inpredict)[0])).encode('ascii')
		
		mpredict.append({'Movie' : mtitle})
		return jsonify(results=mpredict)
	except:
		return jsonify(ecode="Error")


port = os.getenv('PORT', '5000')
if __name__ == "__main__":
	app.run(host='0.0.0.0', port=int(port))

