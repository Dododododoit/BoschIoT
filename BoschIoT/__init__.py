import flask

app = flask.Flask(__name__) 
app.config.from_object('BoschIoT.config')
app.config.from_envvar('BOSCHIOT_SETTINGS', silent=True)
import BoschIoT.views  
import BoschIoT.model  
