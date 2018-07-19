import os
import shutil
import tempfile
import hashlib
import flask
from flask import request, redirect, url_for, session, abort
import arrow
import BoschIoT
import time



@BoschIoT.app.route('/', methods=['GET', 'POST'])
def show_index():
    context = {}
    data = BoschIoT.model.get_db()
    #temp
    context["tempData"] = []
    res = data.execute('SELECT * FROM temperature\
            ORDER BY ctime DESC\
            LIMIT 5')
    for cur in res:
        post_dic = dict()
        post_dic['deviceID'] = cur['deviceID']
        post_dic['temperatureValue'] = cur['temperatureValue']
        post_dic['ctime'] = cur['ctime']
        context['tempData'].append(post_dic)
    #CO2
    context["CO2Data"] = []
    res = data.execute('SELECT * FROM carbonDioxide\
            ORDER BY ctime DESC\
            LIMIT 5')
    for cur in res:
        post_dic = dict()
        post_dic['deviceID'] = cur['deviceID']
        post_dic['CO2value'] = cur['CO2value']
        post_dic['ctime'] = cur['ctime']
        context['CO2Data'].append(post_dic)
    #light
    context["lightData"] = []
    res = data.execute('SELECT * FROM light\
            ORDER BY ctime DESC\
            LIMIT 5')
    for cur in res:
        post_dic = dict()
        post_dic['deviceID'] = cur['deviceID']
        post_dic['lightValue'] = cur['lightValue']
        post_dic['ctime'] = cur['ctime']
        context['lightData'].append(post_dic)
    #humidity
    context["humidityData"] = []
    res = data.execute('SELECT * FROM humidity\
            ORDER BY ctime DESC\
            LIMIT 5')
    for cur in res:
        post_dic = dict()
        post_dic['deviceID'] = cur['deviceID']
        post_dic['humidityValue'] = cur['humidityValue']
        post_dic['ctime'] = cur['ctime']
        context['humidityData'].append(post_dic)
    return flask.render_template("index.html", **context)


@BoschIoT.app.route('/update/temperature', methods=['POST'])
def update_temperature():
    context = {}
    data = BoschIoT.model.get_db()
    #temp
    id = request.form['deviceID']
    value = request.form['temperatureValue']
    res = data.execute('INSERT INTO temperature(deviceID,temperatureValue)\
            VALUES(?, ?)\
            ', [id, value])
    if int(value) >28:
        res = data.execute('UPDATE DeviceStatus SET Fans = 1 WHERE deviceID = ' + str(id))  
    else:
        res = data.execute('UPDATE DeviceStatus SET Fans = 0 WHERE deviceID = ' + str(id))  
    data.commit()
    return flask.jsonify(**context), 200

@BoschIoT.app.route('/update/CO2', methods=['POST'])
def update_CO2():
    context = {}
    data = BoschIoT.model.get_db()
    #temp
    id = request.form['deviceID']
    value = request.form['CO2value']
    res = data.execute('INSERT INTO carbonDioxide(deviceID,CO2value)\
            VALUES(?, ?)\
            ', [id, value])
    if int(value) >500:
        res = data.execute('UPDATE DeviceStatus SET Curtain = 0 WHERE deviceID = ' + str(id))  
    else:
        res = data.execute('UPDATE DeviceStatus SET Curtain = 1 WHERE deviceID = ' + str(id))  
    data.commit()
    return flask.jsonify(**context), 200

@BoschIoT.app.route('/update/light', methods=['POST'])
def update_light():
    context = {}
    data = BoschIoT.model.get_db()
    #temp
    id = request.form['deviceID']
    value = request.form['lightValue']
    res = data.execute('INSERT INTO light(deviceID,lightValue)\
            VALUES(?, ?)\
            ', [id, value])
    if int(value) <=200:
        res = data.execute('UPDATE DeviceStatus SET LED = 1 WHERE deviceID = ' + str(id))  
    else:
        res = data.execute('UPDATE DeviceStatus SET LED = 0 WHERE deviceID = ' + str(id))  
    data.commit()
    return flask.jsonify(**context), 200


@BoschIoT.app.route('/update/humidity', methods=['POST'])
def update_humidity():
    context = {}
    data = BoschIoT.model.get_db()
    #temp
    id = request.form['deviceID']
    value = request.form['humidityValue']
    res = data.execute('INSERT INTO humidity(deviceID,humidityValue)\
            VALUES(?, ?)\
            ', [id, value])
    data.commit()
    return flask.jsonify(**context), 200


@BoschIoT.app.route('/deviceStatus', methods=['GET'])
def get_device_status():
    context = {}
    data = BoschIoT.model.get_db()
    #temp
    id = 1
    res = data.execute('SELECT * FROM DeviceStatus WHERE deviceID = ' + str(id)).fetchone()
    if res:
        context["deviceID"] = res["deviceID"]
        context["deviceType"] = res["deviceType"]
        context["Curtain"] = res["Curtain"]
        context["Fans"] = res["Fans"]
        context["LED"] = res["LED"]
    else:
        res = data.execute('INSERT INTO DeviceStatus(deviceID, deviceType)\
            VALUES(?, ?)\
            ', [id, id])
        context["deviceID"] = id
        context["deviceType"] = id
        context["Curtain"] = 0
        context["Fans"] = 0
        context["LED"] = 0
        
    data.commit()
    return flask.jsonify(**context), 200

@BoschIoT.app.route('/homePage', methods=['GET'])
def get_home_page():
    context = {}
    return flask.render_template("homePage.html", **context)


@BoschIoT.app.route('/deviceCharts/<id>', methods=['GET'])
def get_device_charts(id):
    context = {}
    data = BoschIoT.model.get_db()
    #temp
    context["id"] = id
    return flask.render_template("deviceMonitor.html", **context)

@BoschIoT.app.route('/TempChart/<id>', methods=['GET'])
def get_temp_charts(id):
    context = {}
    data = BoschIoT.model.get_db()
    #temp
    context["id"] = id
    return flask.render_template("TemperatureChart.html", **context)

@BoschIoT.app.route('/charts/tempData/<id>', methods=['GET'])
def get_temp_data(id):
    context = {}
    data = BoschIoT.model.get_db()
    #temp
    context["id"] = id
    tempData = []
    for i in range(24):
        # print('SELECT AVG(o.temperatureValue) AVGTEMP FROM temperature o WHERE o.ctime >DATE_SUB(CURDATE(), INTERVAL ' + str(24 - i) + ' HOUR) AND o.ctime < DATE_SUB(CURDATE(), INTERVAL ' +str(23 - i)+ ' HOUR)')
        res = data.execute("SELECT AVG(o.temperatureValue) AS AVGTEMP FROM temperature o WHERE o.ctime >DATETIME( 'now', 'localtime', '-" + str(24 - i) + " hour')\
         AND o.ctime <= DATETIME( 'now', 'localtime', '-" + str(23 - i) + " hour') AND o.deviceID = " + str(id))
        newData = 0
        print("SELECT AVG(o.temperatureValue) AS AVGTEMP FROM temperature o WHERE o.ctime >DATETIME( 'now','localtime', '-" + str(24 - i) + " hour')\
         AND o.ctime <= DATETIME( 'now', 'localtime', '-" + str(23 - i) + " hour') AND o.deviceID = " + str(id))
        for cur in res:
            newData = cur["AVGTEMP"]
        if newData == None:
            newData = 0
        tempData.append(newData)
        print(newData)
    context["datay"] = tempData
    return flask.jsonify(**context), 200


@BoschIoT.app.route('/CO2Chart/<id>', methods=['GET'])
def get_CO2_charts(id):
    context = {}
    data = BoschIoT.model.get_db()
    #temp
    context["id"] = id
    return flask.render_template("CO2Chart.html", **context)


@BoschIoT.app.route('/charts/CO2Data/<id>', methods=['GET'])
def get_CO2_data(id):
    context = {}
    data = BoschIoT.model.get_db()
    #temp
    context["id"] = id
    tempData = []
    for i in range(24):
        # print('SELECT AVG(o.temperatureValue) AVGTEMP FROM temperature o WHERE o.ctime >DATE_SUB(CURDATE(), INTERVAL ' + str(24 - i) + ' HOUR) AND o.ctime < DATE_SUB(CURDATE(), INTERVAL ' +str(23 - i)+ ' HOUR)')
        res = data.execute("SELECT AVG(o.CO2value) AS AVGTEMP FROM carbonDioxide o WHERE o.ctime >DATETIME( 'now', 'localtime', '-" + str(24 - i) + " hour')\
         AND o.ctime <= DATETIME( 'now', 'localtime', '-" + str(23 - i) + " hour') AND o.deviceID = " + str(id))
        newData = 0
        print("SELECT AVG(o.CO2value) AS AVGTEMP FROM carbonDioxide o WHERE o.ctime >DATETIME( 'now','localtime', '-" + str(24 - i) + " hour')\
         AND o.ctime <= DATETIME( 'now', 'localtime', '-" + str(23 - i) + " hour') AND o.deviceID = " + str(id))
        for cur in res:
            newData = cur["AVGTEMP"]
        if newData == None:
            newData = 0
        tempData.append(newData)
        print(newData)
    context["datay"] = tempData
    return flask.jsonify(**context), 200


@BoschIoT.app.route('/lightChart/<id>', methods=['GET'])
def get_light_charts(id):
    context = {}
    data = BoschIoT.model.get_db()
    #temp
    context["id"] = id
    return flask.render_template("lightChart.html", **context)


@BoschIoT.app.route('/charts/lightData/<id>', methods=['GET'])
def get_light_data(id):
    context = {}
    data = BoschIoT.model.get_db()
    #temp
    context["id"] = id
    tempData = []
    for i in range(24):
        # print('SELECT AVG(o.temperatureValue) AVGTEMP FROM temperature o WHERE o.ctime >DATE_SUB(CURDATE(), INTERVAL ' + str(24 - i) + ' HOUR) AND o.ctime < DATE_SUB(CURDATE(), INTERVAL ' +str(23 - i)+ ' HOUR)')
        res = data.execute("SELECT AVG(o.lightValue) AS AVGTEMP FROM light o WHERE o.ctime >DATETIME( 'now', 'localtime', '-" + str(24 - i) + " hour')\
         AND o.ctime <= DATETIME( 'now', 'localtime', '-" + str(23 - i) + " hour') AND o.deviceID = " + str(id))
        newData = 0
        print("SELECT AVG(o.lightValue) AS AVGTEMP FROM light o WHERE o.ctime >DATETIME( 'now','localtime', '-" + str(24 - i) + " hour')\
         AND o.ctime <= DATETIME( 'now', 'localtime', '-" + str(23 - i) + " hour') AND o.deviceID = " + str(id))
        for cur in res:
            newData = cur["AVGTEMP"]
        if newData == None:
            newData = 0
        tempData.append(newData)
        print(newData)
    context["datay"] = tempData
    return flask.jsonify(**context), 200


@BoschIoT.app.route('/humidityChart/<id>', methods=['GET'])
def get_humidity_charts(id):
    context = {}
    data = BoschIoT.model.get_db()
    #temp
    context["id"] = id
    return flask.render_template("humidityChart.html", **context)


@BoschIoT.app.route('/charts/humidityData/<id>', methods=['GET'])
def get_humidity_data(id):
    context = {}
    data = BoschIoT.model.get_db()
    #temp
    context["id"] = id
    tempData = []
    for i in range(24):
        # print('SELECT AVG(o.temperatureValue) AVGTEMP FROM temperature o WHERE o.ctime >DATE_SUB(CURDATE(), INTERVAL ' + str(24 - i) + ' HOUR) AND o.ctime < DATE_SUB(CURDATE(), INTERVAL ' +str(23 - i)+ ' HOUR)')
        res = data.execute("SELECT AVG(o.humidityValue) AS AVGTEMP FROM humidity o WHERE o.ctime >DATETIME( 'now', 'localtime', '-" + str(24 - i) + " hour')\
         AND o.ctime <= DATETIME( 'now', 'localtime', '-" + str(23 - i) + " hour') AND o.deviceID = " + str(id))
        newData = 0
        print("SELECT AVG(o.humidityValue) AS AVGTEMP FROM humidity o WHERE o.ctime >DATETIME( 'now','localtime', '-" + str(24 - i) + " hour')\
         AND o.ctime <= DATETIME( 'now', 'localtime', '-" + str(23 - i) + " hour') AND o.deviceID = " + str(id))
        for cur in res:
            newData = cur["AVGTEMP"]
        if newData == None:
            newData = 0
        tempData.append(newData)
        print(newData)
    context["datay"] = tempData
    return flask.jsonify(**context), 200
