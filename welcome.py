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
obj_tuple = conn.get_object("Analytics", 'pred_c.gz')

with open('pred_c.gz', 'w') as dl_model:
    dl_model.write(obj_tuple[1])

rf_c = joblib.load('pred_c.gz')
obj_tuple = conn.get_object("Analytics", 'pred_p.gz')

with open('pred_p.gz', 'w') as dl_model:
    dl_model.write(obj_tuple[1])

rf_p = joblib.load('pred_p.gz')

listFcst = []
listRecom = []

dataLock = threading.Lock()
weatherThread = threading.Thread()

def getWeather():
    global weatherThread
    global dataLock
    global listFcst
    global listRecom

    with dataLock:
        listFcst = []
        listRecom = []
        recom = []
        data = json.loads(requests.get("https://api.weather.com/v1/location/92021:4:US/forecast/hourly/24hour.json?language=en-US&units=e&apiKey=565e437c58b7bae616120325e29fd340").text)
        for item in data['forecasts']:
            inpredict = [int(dateutil.parser.parse(item['fcst_valid_local']).time().strftime("%H")),item['dewpt'],item['feels_like'],item['hi'],item['pop'],item['mslp'],item['rh'],item['temp'],item['uv_index'],item['vis'],item['wspd']]
            inpredict = numpy.array(inpredict).reshape(1, (len(inpredict)))	
            ppower = rf_p.predict(inpredict)[0]
            pcons = rf_c.predict(inpredict)[0]
            listFcst.append({'Consumption' : pcons,'Power' : ppower, 'Icon': item['icon_code'], 'Temp' :item['temp'], 'Hour' : dateutil.parser.parse(item['fcst_valid_local']).time().strftime("%I%p"), 'Day' :  item['dow'] })
            recom.append([int(dateutil.parser.parse(item['fcst_valid_local']).time().strftime("%H")), pcons-ppower])

        rates =[0.25,0.25,0.25,0.25,0.25,0.25,0.28,0.32,0.32,0.34,0.36,0.36,0.36,0.36,0.36,0.36,0.36,0.28,0.25,0.25,0.25,0.25,0.25,0.25]

        rd = sorted(recom,key=lambda l:l[1], reverse=True)
        ru = sorted(recom,key=lambda l:l[1], reverse=False)

        for x in range(0, 5):
            mtime = abs(rd[x][0]-ru[x][0])
            mwatts = rd[x][1]*0.8
            if (rd[x][1]*0.8 + ru[x][1]) < 0:
                msavings = (rd[x][1]*0.8/1000*rates[rd[x][0]])
            else:
                msavings = (rd[x][1]*0.8/1000*rates[rd[x][0]]) - ((ru[x][1]+(rd[x][1]*0.8))/1000*rates[ru[x][0]])
            mname = "Use " + str(mwatts) + "Wh at " + str(ru[x][0]) + ":00 rather than at " + str(rd[x][0]) + ":00"
            listRecom.append({"key": "m"+str(x),"name": mname, "values": {"power":mwatts,"change":mtime,"savings":msavings}})
            mtime = 0
            mwatts = rd[x][1]*0.3
            msavings = (((rd[x][1]*0.3)/1000)*rates[rd[x][0]])
            mname = "Reduce consumption by " + str(mwatts) + "Wh at " + str(rd[x][0]) + ":00"
            listRecom.append({"key": "r"+str(x),"name": mname, "values": {"power":mwatts,"change":mtime,"savings":msavings}})
    weatherThread = threading.Timer(1800, getWeather, ())
    weatherThread.start()   

getWeather()

@app.route('/')
def notice():
	return "This is a webapp"

@app.route('/predict', methods=['GET', 'POST'])
def parse_request():
	try:
		global listFcst
		return jsonify(results=listFcst)
	except:
		return jsonify(ecode=sys.exc_info()[0])

@app.route('/recom', methods=['GET', 'POST'])
def send_recom():
	try:
		global listRecom
		return jsonify(options=listRecom) 
	except:
		return jsonify(ecode=sys.exc_info()[0])

port = os.getenv('PORT', '5000')
if __name__ == "__main__":
	app.run(host='0.0.0.0', port=int(port))

