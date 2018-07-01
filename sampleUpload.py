# -* - coding: UTF-8 -* -  
import requests

#Modify id and Value here
id = 111
value = 111
data={"deviceID": id, "temperatureValue": value}

response = requests.post('http://18.219.249.109/update/temperature',data=data)
print(response.text)


#Modify id and Value here
id = 111
value = 111
data={"deviceID": id, "CO2value": value}
response = requests.post('http://18.219.249.109/update/CO2',data=data)
print(response.text)


#Modify id and Value here
id = 111
value = 111
data={"deviceID": id, "lightValue": value}
response = requests.post('http://18.219.249.109/update/light',data=data)
print(response.text)

#Modify id and Value here
id = 111
value = 111
data={"deviceID": id, "humidityValue": value}
response = requests.post('http://18.219.249.109/update/humidity',data=data)
print(response.text)