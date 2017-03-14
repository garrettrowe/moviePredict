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

mpredict = []



inpredict = [int(self.request.GET.get('GENDER')),int(self.request.GET.get('SENIORCITIZEN')),int(self.request.GET.get('DEPENDENTS')),int(self.request.GET.get('TENURE')),int(self.request.GET.get('PAPERLESSBILLING')),int(self.request.GET.get('PAYMENTMETHOD'))self.request.GET.get('MONTHLYCHARGES')]
inpredict = numpy.array(inpredict).reshape(1, (len(inpredict)))	
mtitle = movie.predict(inpredict)[0]
mpredict.append({'Movie' : mtitle})

@app.route('/')
def notice():
	return "This is a webapp"

@app.route('/predict', methods=['GET', 'POST'])
def parse_request():
	try:
		global mpredict
		return jsonify(results=mpredict)
	except:
		return jsonify(ecode=sys.exc_info()[0])


port = os.getenv('PORT', '5000')
if __name__ == "__main__":
	app.run(host='0.0.0.0', port=int(port))

