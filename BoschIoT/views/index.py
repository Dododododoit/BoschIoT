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
    res = data.execute('SELECT * FROM DeviceSetting WHERE deviceID = ' + str(id)).fetchone()
    Fans_open = res["FansTemp"]
    Fans_open = int(Fans_open)
    CurtainTemp = res["CurtainTemp"]
    CurtainTemp = int(CurtainTemp)
    res = data.execute('SELECT * FROM AlertThreshold WHERE deviceID = ' + str(id)).fetchone()
    lowTemp= res["tempFloor"]
    lowTemp = int(lowTemp)
    highTemp = res["tempCeil"]
    highTemp = int(highTemp)

    res = data.execute('INSERT INTO temperature(deviceID,temperatureValue)\
            VALUES(?, ?)\
            ', [id, value])



    if int(value) > highTemp:
    	res = data.execute('INSERT INTO AlertLog(deviceID, category, value, alertInfo)\
            VALUES(?, ?, ?, ?)\
            ', [id, 1, int(value), 1])
    elif int(value) < lowTemp:
    	res = data.execute('INSERT INTO AlertLog(deviceID, category, value, alertInfo)\
            VALUES(?, ?, ?, ?)\
            ', [id, 1, int(value), 0])



    if int(value) >CurtainTemp:
        res = data.execute('UPDATE DeviceStatus SET Curtain = 0 WHERE deviceID = ' + str(id))  
    else:
        res = data.execute('UPDATE DeviceStatus SET Curtain = 1 WHERE deviceID = ' + str(id))  
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
    res = data.execute('SELECT * FROM AlertThreshold WHERE deviceID = ' + str(id)).fetchone()
    CO2Floor= res["CO2Floor"]
    CO2Floor = int(CO2Floor)
    CO2Ceil = res["CO2Ceil"]
    CO2Ceil = int(CO2Ceil)
    if int(value) > CO2Ceil:
    	res = data.execute('INSERT INTO AlertLog(deviceID, category, value, alertInfo)\
            VALUES(?, ?, ?, ?)\
            ', [id, 2, int(value), 1])
    elif int(value) < CO2Floor:
    	res = data.execute('INSERT INTO AlertLog(deviceID, category, value, alertInfo)\
            VALUES(?, ?, ?, ?)\
            ', [id, 2, int(value), 0])
    data.commit()
    return flask.jsonify(**context), 200

@BoschIoT.app.route('/update/light', methods=['POST'])
def update_light():
    context = {}
    data = BoschIoT.model.get_db()
    id = request.form['deviceID']
    #setting
    res = data.execute('SELECT * FROM DeviceSetting WHERE deviceID = ' + str(id)).fetchone()
    thd = res["LEDLight"]
    thd = int(thd)
    #temp
    id = request.form['deviceID']
    value = request.form['lightValue']


    res = data.execute('SELECT * FROM AlertThreshold WHERE deviceID = ' + str(id)).fetchone()
    lightFloor= res["lightFloor"]
    lightFloor = int(lightFloor)
    lightCeil = res["lightCeil"]
    lightCeil = int(lightCeil)
    if int(value) > lightCeil:
    	res = data.execute('INSERT INTO AlertLog(deviceID, category, value, alertInfo)\
            VALUES(?, ?, ?, ?)\
            ', [id, 3, int(value), 1])
    elif int(value) < lightFloor:
    	res = data.execute('INSERT INTO AlertLog(deviceID, category, value, alertInfo)\
            VALUES(?, ?, ?, ?)\
            ', [id, 3, int(value), 0])

    res = data.execute('INSERT INTO light(deviceID,lightValue)\
            VALUES(?, ?)\
            ', [id, value])

    if int(value) <=thd:
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


    res = data.execute('SELECT * FROM DeviceSetting WHERE deviceID = ' + str(id)).fetchone()
    Fans_open = res["FansTemp"]
    Fans_open = int(Fans_open)



    res = data.execute('SELECT * FROM AlertThreshold WHERE deviceID = ' + str(id)).fetchone()
    humidityFloor= res["humidityFloor"]
    humidityFloor = int(humidityFloor)
    humidityCeil = res["humidityCeil"]
    humidityCeil = int(humidityCeil)
    if int(value) > humidityCeil:
    	res = data.execute('INSERT INTO AlertLog(deviceID, category, value, alertInfo)\
            VALUES(?, ?, ?, ?)\
            ', [id, 4, int(value), 1])
    elif int(value) < humidityFloor:
    	res = data.execute('INSERT INTO AlertLog(deviceID, category, value, alertInfo)\
            VALUES(?, ?, ?, ?)\
            ', [id, 4, int(value), 0])


    if int(value) >Fans_open:
        res = data.execute('UPDATE DeviceStatus SET Fans = 1 WHERE deviceID = ' + str(id))  
    else:
        res = data.execute('UPDATE DeviceStatus SET Fans = 0 WHERE deviceID = ' + str(id))  
    data.commit()
    return flask.jsonify(**context), 200


@BoschIoT.app.route('/deviceStatus', methods=['GET'])
def get_device_status():
    context = {}
    data = BoschIoT.model.get_db()
    #temp
    id = int(request.form['id'])
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


@BoschIoT.app.route('/DeviceSetting/<id>', methods=['GET'])
def get_Device_Setting(id):
    context = {}
    data = BoschIoT.model.get_db()
    #temp
    context["id"] = int(id)
    res = data.execute('SELECT * FROM DeviceSetting WHERE deviceID = ' + str(id)).fetchone()
    if res:
        context["deviceID"] = res["deviceID"]
        context["deviceType"] = res["deviceType"]
        context["CurtainTemp"] = res["CurtainTemp"]
        context["FansTemp"] = res["FansTemp"]
        context["LEDLight"] = res["LEDLight"]
    else:
        res = data.execute('INSERT INTO DeviceSetting(deviceID, deviceType)\
            VALUES(?, ?)\
            ', [id, id])
        context["deviceID"] = id
        context["deviceType"] = id
        context["CurtainTemp"] = 10
        context["FansTemp"] = 500
        context["LEDLight"] = 200
        
    data.commit()
    return flask.render_template("Setting.html", **context)



@BoschIoT.app.route('/update/curtain_threashold/<id>', methods=['POST'])
def set_curtain_temp(id):
    context = {}
    data = BoschIoT.model.get_db()
    #temp
    id = int(id)
    value = request.form['fname']
    res = data.execute('UPDATE DeviceSetting SET CurtainTemp = ' + str(value)+ ' WHERE deviceID = ' + str(id))
    return flask.redirect(url_for('get_Device_Setting', id=1))

@BoschIoT.app.route('/update/fans_threashold/<id>', methods=['POST'])
def set_fans_temp(id):
    context = {}
    data = BoschIoT.model.get_db()
    #temp
    id = int(id)
    value = request.form['fname']
    res = data.execute('UPDATE DeviceSetting SET FansTemp = ' + str(value)+ ' WHERE deviceID = ' + str(id))
    return flask.redirect(url_for('get_Device_Setting', id=1))

@BoschIoT.app.route('/update/LED_threashold/<id>', methods=['POST'])
def set_led_temp(id):
    context = {}
    data = BoschIoT.model.get_db()
    #temp
    id = int(id)
    value = request.form['fname']
    res = data.execute('UPDATE DeviceSetting SET LEDLight = ' + str(value)+ ' WHERE deviceID = ' + str(id))
    return flask.redirect(url_for('get_Device_Setting', id=id))


@BoschIoT.app.route('/AlertSetting/<id>', methods=['GET'])
def get_Alert_Setting(id):
    context = {}
    data = BoschIoT.model.get_db()
    #temp
    context["id"] = int(id)
    res = data.execute('SELECT * FROM AlertThreshold WHERE deviceID = ' + str(id)).fetchone()
    if res:
        context["deviceID"] = res["deviceID"]
        context["deviceType"] = res["deviceType"]
        context["tempFloor"] = res["tempFloor"]
        context["tempCeil"] = res["tempCeil"]
        context["CO2Floor"] = res["CO2Floor"]
        context["CO2Ceil"] = res["CO2Ceil"]
        context["lightFloor"] = res["lightFloor"]
        context["lightCeil"] = res["lightCeil"]
        context["humidityFloor"] = res["humidityFloor"]
        context["humidityCeil"] = res["humidityCeil"]
    else:
        res = data.execute('INSERT INTO AlertThreshold(deviceID, deviceType)\
            VALUES(?, ?)\
            ', [id, id])
        context["deviceID"] = id
        context["deviceType"] = id
        context["tempFloor"] = 0
        context["tempCeil"] = 999
        context["CO2Floor"] = 0
        context["CO2Ceil"] = 999
        context["lightFloor"] = 0
        context["lightCeil"] = 999
        context["humidityFloor"] = 0
        context["humidityCeil"] = 999
        print("create entry")
        
    data.commit()
    return flask.render_template("AlertSetting.html", **context)


@BoschIoT.app.route('/update/temp_threashold/<id>', methods=['POST'])
def set_thd_temp(id):
    context = {}
    data = BoschIoT.model.get_db()
    #temp
    id = int(id)
    value1 = request.form['fname1']
    value2 = request.form['fname2']
    res = data.execute('UPDATE AlertThreshold	 SET tempFloor = ' + str(value1)+ ' 	, tempCeil = ' + str(value2) + ' WHERE deviceID = ' + str(id))
    #print('UPDATE AlertThreshold	 SET tempFloor = ' + str(value1)+ ' 	AND tempCeil = ' + str(value2) + ' WHERE deviceID = ' + str(id))
    return flask.redirect(url_for('get_Alert_Setting', id=id))


@BoschIoT.app.route('/update/CO2_threashold/<id>', methods=['POST'])
def set_thd_CO2(id):
    context = {}
    data = BoschIoT.model.get_db()
    #temp
    id = int(id)
    value1 = request.form['fname1']
    value2 = request.form['fname2']
    res = data.execute('UPDATE AlertThreshold	 SET CO2Floor = ' + str(value1)+ ' 	, CO2Ceil = ' + str(value2) + ' WHERE deviceID = ' + str(id))
    #print('UPDATE AlertThreshold	 SET tempFloor = ' + str(value1)+ ' 	AND tempCeil = ' + str(value2) + ' WHERE deviceID = ' + str(id))
    return flask.redirect(url_for('get_Alert_Setting', id=id))


@BoschIoT.app.route('/update/light_threashold/<id>', methods=['POST'])
def set_thd_light(id):
    context = {}
    data = BoschIoT.model.get_db()
    #temp
    id = int(id)
    value1 = request.form['fname1']
    value2 = request.form['fname2']
    res = data.execute('UPDATE AlertThreshold	 SET lightFloor = ' + str(value1)+ ' 	, lightCeil = ' + str(value2) + ' WHERE deviceID = ' + str(id))
    #print('UPDATE AlertThreshold	 SET tempFloor = ' + str(value1)+ ' 	AND tempCeil = ' + str(value2) + ' WHERE deviceID = ' + str(id))
    return flask.redirect(url_for('get_Alert_Setting', id=id))

@BoschIoT.app.route('/update/humidity_threashold/<id>', methods=['POST'])
def set_thd_humidity(id):
    context = {}
    data = BoschIoT.model.get_db()
    #temp
    id = int(id)
    value1 = request.form['fname1']
    value2 = request.form['fname2']
    res = data.execute('UPDATE AlertThreshold	 SET humidityFloor = ' + str(value1)+ ' 	, humidityCeil = ' + str(value2) + ' WHERE deviceID = ' + str(id))
    #print('UPDATE AlertThreshold	 SET tempFloor = ' + str(value1)+ ' 	AND tempCeil = ' + str(value2) + ' WHERE deviceID = ' + str(id))
    return flask.redirect(url_for('get_Alert_Setting', id=id))


@BoschIoT.app.route('/AlertLog/<id>', methods=['GET'])
def get_Alert_Log(id):
    context = {}
    data = BoschIoT.model.get_db()
    #temp
    context["id"] = int(id)
    data.commit()
    return flask.render_template("AlertLogging.html", **context)


@BoschIoT.app.route('/AlertLog/detail/<id>', methods=['GET'])
def get_Alert_detail_Log(id):
    context = {}
    data = BoschIoT.model.get_db()
    #temp
    page = int(request.args.get('page'))#int(request.form['page'])
    limit = int(request.args.get('limit'))#int(request.form['limit'])
    context["id"] = int(id)
    context["code"] = 0
    context["msg"] = ""
    context["count"] = 10
    context["data"] = []
    res = data.execute('SELECT count(*) AS ct FROM AlertLog WHERE deviceID = ' + str(id)).fetchone()
    context["count"] = res["ct"]
    sql_str = 'SELECT * FROM AlertLog WHERE deviceID = ' + str(id);
    sql_str += " ORDER BY timeline DESC "
    if int(page) == 1:
        lim_str = 'limit ' + str(limit)
    else:
        lim_str = 'limit ' + str((int(page)-1)*int(limit)) + ',' +str(limit)
    sql_str += lim_str
    res = data.execute(sql_str)
    for cur in res:
        post_dic = dict()
        post_dic['value'] = cur['value']
        post_dic['time'] = cur['timeline']
        if cur['category']==1:
            post_dic['category'] = "Temperature"
        elif cur['category']==2:
            post_dic['category'] = "CO2"
        elif cur['category']==3:
            post_dic['category'] = "Light"
        elif cur['category']==4:
            post_dic['category'] = "Humidity"
        post_dic['info'] = cur['alertInfo']
        if cur['alertInfo']==0:
            post_dic['info'] = "low"
        elif cur['alertInfo']==1:
            post_dic['info'] = "high"
        context['data'].append(post_dic)
    data.commit()
    return flask.jsonify(**context), 200


@BoschIoT.app.route('/home', methods=['GET'])
def get_home():
    context = {}
    data = BoschIoT.model.get_db()
    data.commit()
    context["temp1"] = 100
    context["CO21"] = 100
    context["humidity1"] = 100
    context["light1"] = 100
    #context["color1"] = "gray"
    context["status1"] = "Normal"
    res = data.execute('SELECT * FROM temperature\
            WHERE deviceID = 1\
            ORDER BY ctime DESC\
            LIMIT 1').fetchone()
    if res:
        context["temp1"] = res["temperatureValue"]
        res = data.execute('SELECT * FROM AlertThreshold WHERE deviceID = 1').fetchone()
        lowTemp= res["tempFloor"]
        lowTemp = int(lowTemp)
        highTemp = res["tempCeil"]
        highTemp = int(highTemp)
        if int(context["temp1"]) > highTemp: 
            context["status1"] = "Alert"
        elif int(context["temp1"]) < lowTemp:
            context["status1"] = "Alert"
    else:
        context["temp1"] = "None"
    res = data.execute('SELECT * FROM carbonDioxide\
            WHERE deviceID = 1\
            ORDER BY ctime DESC\
            LIMIT 1').fetchone()
    if res:
        context["CO21"] = res["CO2value"]

        res = data.execute('SELECT * FROM AlertThreshold WHERE deviceID = 1').fetchone()
        CO2Floor= res["CO2Floor"]
        CO2Floor = int(CO2Floor)
        CO2Ceil = res["CO2Ceil"]
        CO2Ceil = int(CO2Ceil)
        if int(context["CO21"]) > CO2Ceil: 
            context["status1"] = "Alert"
        elif int(context["CO21"]) < CO2Floor:
            context["status1"] = "Alert"

    else:
        context["CO21"] = "None"
    res = data.execute('SELECT * FROM light\
            WHERE deviceID = 1\
            ORDER BY ctime DESC\
            LIMIT 1').fetchone()
    if res:
        context["light1"] = res["lightValue"]


        res = data.execute('SELECT * FROM AlertThreshold WHERE deviceID = 1').fetchone()
        lightFloor= res["lightFloor"]
        lightFloor = int(lightFloor)
        lightCeil = res["lightCeil"]
        lightCeil = int(lightCeil)
        if int(context["light1"]) > lightCeil: 
            context["status1"] = "Alert"
        elif int(context["light1"]) < lightFloor:
            context["status1"] = "Alert"
    else:
        context["light1"] = "None"
    res = data.execute('SELECT * FROM humidity\
            WHERE deviceID = 1\
            ORDER BY ctime DESC\
            LIMIT 1').fetchone()
    if res:
        context["humidity1"] = res["humidityValue"]
        res = data.execute('SELECT * FROM AlertThreshold WHERE deviceID = 1').fetchone()
        humidityFloor= res["humidityFloor"]
        humidityFloor = int(humidityFloor)
        humidityCeil = res["humidityCeil"]
        humidityCeil = int(humidityCeil)
        if int(context["humidity1"]) > humidityCeil: 
            context["status1"] = "Alert"
        elif int(context["humidity1"]) < humidityFloor:
            context["status1"] = "Alert"
    else:
        context["humidity1"] = "None"















    context["temp2"] = 100
    context["CO22"] = 100
    context["humidity2"] = 100
    context["light2"] = 100
    #context["color1"] = "gray"
    context["status2"] = "Normal"
    res = data.execute('SELECT * FROM temperature\
            WHERE deviceID = 2\
            ORDER BY ctime DESC\
            LIMIT 1').fetchone()
    if res:
        context["temp2"] = res["temperatureValue"]
        res = data.execute('SELECT * FROM AlertThreshold WHERE deviceID = 2').fetchone()
        lowTemp= res["tempFloor"]
        lowTemp = int(lowTemp)
        highTemp = res["tempCeil"]
        highTemp = int(highTemp)
        if int(context["temp2"]) > highTemp: 
            context["status2"] = "Alert"
        elif int(context["temp2"]) < lowTemp:
            context["status2"] = "Alert"
    else:
        context["temp2"] = "None"
    res = data.execute('SELECT * FROM carbonDioxide\
            WHERE deviceID = 2\
            ORDER BY ctime DESC\
            LIMIT 1').fetchone()
    if res:
        context["CO22"] = res["CO2value"]


        res = data.execute('SELECT * FROM AlertThreshold WHERE deviceID = 2').fetchone()
        CO2Floor= res["CO2Floor"]
        CO2Floor = int(CO2Floor)
        CO2Ceil = res["CO2Ceil"]
        CO2Ceil = int(CO2Ceil)
        if int(context["CO22"]) > CO2Ceil: 
            context["status2"] = "Alert"
        elif int(context["CO22"]) < CO2Floor:
            context["status2"] = "Alert"


    else:
        context["CO22"] = "None"
    res = data.execute('SELECT * FROM light\
            WHERE deviceID = 2\
            ORDER BY ctime DESC\
            LIMIT 1').fetchone()
    if res:
        context["light2"] = res["lightValue"]
        res = data.execute('SELECT * FROM AlertThreshold WHERE deviceID = 2').fetchone()
        lightFloor= res["lightFloor"]
        lightFloor = int(lightFloor)
        lightCeil = res["lightCeil"]
        lightCeil = int(lightCeil)
        if int(context["light2"]) > lightCeil: 
            context["status2"] = "Alert"
        elif int(context["light2"]) < lightFloor:
            context["status2"] = "Alert"


    else:
        context["light2"] = "None"
    res = data.execute('SELECT * FROM humidity\
            WHERE deviceID = 2\
            ORDER BY ctime DESC\
            LIMIT 1').fetchone()
    if res:
        context["humidity2"] = res["humidityValue"]
        res = data.execute('SELECT * FROM AlertThreshold WHERE deviceID = 2').fetchone()
        humidityFloor= res["humidityFloor"]
        humidityFloor = int(humidityFloor)
        humidityCeil = res["humidityCeil"]
        humidityCeil = int(humidityCeil)
        if int(context["humidity2"]) > humidityCeil: 
            context["status2"] = "Alert"
        elif int(context["humidity2"]) < humidityFloor:
            context["status2"] = "Alert"
    else:
        context["humidity2"] = "None"


















    context["temp3"] = 100
    context["CO23"] = 100
    context["humidity3"] = 100
    context["light3"] = 100
    #context["color1"] = "gray"
    context["status3"] = "Normal"
    res = data.execute('SELECT * FROM temperature\
            WHERE deviceID = 3\
            ORDER BY ctime DESC\
            LIMIT 1').fetchone()
    if res:
        context["temp3"] = res["temperatureValue"]
        res = data.execute('SELECT * FROM AlertThreshold WHERE deviceID = 3').fetchone()
        lowTemp= res["tempFloor"]
        lowTemp = int(lowTemp)
        highTemp = res["tempCeil"]
        highTemp = int(highTemp)
        if int(context["temp3"]) > highTemp: 
            context["status3"] = "Alert"
        elif int(context["temp3"]) < lowTemp:
            context["status3"] = "Alert"
    else:
        context["temp3"] = "None"

    res = data.execute('SELECT * FROM carbonDioxide\
            WHERE deviceID = 3\
            ORDER BY ctime DESC\
            LIMIT 1').fetchone()
    if res:
        context["CO23"] = res["CO2value"]


        res = data.execute('SELECT * FROM AlertThreshold WHERE deviceID = 3').fetchone()
        CO2Floor= res["CO2Floor"]
        CO2Floor = int(CO2Floor)
        CO2Ceil = res["CO2Ceil"]
        CO2Ceil = int(CO2Ceil)
        if int(context["CO23"]) > CO2Ceil: 
            context["status3"] = "Alert"
        elif int(context["CO23"]) < CO2Floor:
            context["status3"] = "Alert"


    else:
        context["CO23"] = "None"
    res = data.execute('SELECT * FROM light\
            WHERE deviceID = 3\
            ORDER BY ctime DESC\
            LIMIT 1').fetchone()
    if res:
        context["light3"] = res["lightValue"]
        res = data.execute('SELECT * FROM AlertThreshold WHERE deviceID = 3').fetchone()
        lightFloor= res["lightFloor"]
        lightFloor = int(lightFloor)
        lightCeil = res["lightCeil"]
        lightCeil = int(lightCeil)
        if int(context["light3"]) > lightCeil: 
            context["status3"] = "Alert"
        elif int(context["light3"]) < lightFloor:
            context["status3"] = "Alert"

    else:
        context["light3"] = "None"
    res = data.execute('SELECT * FROM humidity\
            WHERE deviceID = 3\
            ORDER BY ctime DESC\
            LIMIT 1').fetchone()
    if res:
        context["humidity3"] = res["humidityValue"]
        res = data.execute('SELECT * FROM AlertThreshold WHERE deviceID = 3').fetchone()
        humidityFloor= res["humidityFloor"]
        humidityFloor = int(humidityFloor)
        humidityCeil = res["humidityCeil"]
        humidityCeil = int(humidityCeil)
        if int(context["humidity3"]) > humidityCeil: 
            context["status3"] = "Alert"
        elif int(context["humidity3"]) < humidityFloor:
            context["status3"] = "Alert"
    else:
        context["humidity3"] = "None"



    if context["status1"] == "Normal":
        context["newcolorA"] = "green"
    else:
        context["newcolorA"] = "red"

    if context["status2"] == "Normal":
        context["newcolorB"] = "green"
    else:
        context["newcolorB"] = "red"

    if context["status3"] == "Normal":
        context["newcolorC"] = "green"
    else:
        context["newcolorC"] = "red"



    return flask.render_template("gateway.html", **context)
