CREATE TABLE temperature (
  deviceID VARCHAR(20) NOT NULL,
  temperatureValue FLOAT DEFAULT NULL,
  ctime TIMESTAMP DEFAULT (datetime('now', 'localtime')),
  abnormal INTEGER DEFAULT 0
);

CREATE TABLE carbonDioxide (
  deviceID VARCHAR(20) NOT NULL,
  CO2value FLOAT DEFAULT NULL,
  ctime TIMESTAMP DEFAULT (datetime('now', 'localtime')),
  abnormal INTEGER DEFAULT 0
);

CREATE TABLE light (
  deviceID VARCHAR(20) NOT NULL,
  lightValue INTEGER DEFAULT NULL,
  ctime TIMESTAMP DEFAULT (datetime('now', 'localtime')),
  abnormal INTEGER DEFAULT 0
);

CREATE TABLE humidity (
  deviceID VARCHAR(20) NOT NULL,
  humidityValue FLOAT DEFAULT NULL,
  ctime TIMESTAMP DEFAULT (datetime('now', 'localtime')),
  abnormal INTEGER DEFAULT 0
);

CREATE TABLE DeviceStatus (
  deviceID VARCHAR(20) NOT NULL,
  deviceType VARCHAR(20) DEFAULT NULL,
  Curtain INTEGER DEFAULT 0,
  Fans INTEGER DEFAULT 0,
  LED INTEGER DEFAULT 0
);

CREATE TABLE DeviceSetting (
  deviceID VARCHAR(20) NOT NULL,
  deviceType VARCHAR(20) DEFAULT NULL,
  CurtainTemp FLOAT DEFAULT 10,
  FansTemp FLOAT DEFAULT 35,
  LEDLight INTEGER DEFAULT 200
);


CREATE TABLE AlertThreshold (
  deviceID VARCHAR(20) NOT NULL,
  deviceType VARCHAR(20) DEFAULT NULL,
  tempFloor FLOAT DEFAULT 0,
  tempCeil FLOAT DEFAULT 999,
  CO2Floor FLOAT DEFAULT 0,
  CO2Ceil FLOAT DEFAULT 999,
  lightFloor INTEGER DEFAULT 0,
  lightCeil INTEGER DEFAULT 999,
  humidityFloor FLOAT DEFAULT 0,
  humidityCeil FLOAT DEFAULT 999
);

CREATE TABLE AlertLog (
  deviceID VARCHAR(20) NOT NULL,
  category INTEGER DEFAULT 10,
  timeline TIMESTAMP DEFAULT (datetime('now', '+8 hour')),
  value FLOAT DEFAULT 0,
  alertInfo INTEGER DEFAULT 0
);