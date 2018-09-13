
CREATE SCHEMA WEATHER;
CREATE TABLE WEATHER.WEATHER (
    tsa bigint primary key, 
    time timestamp, 
    temperature real, 
    humidity real, 
    pressure real, 
    light real,
    fw_version char(10),
    sw_version char(10),
    version char(10),
    isThermometer boolean,
    isBarometer boolean,
    isHygrometer boolean,
    isClock boolean
    );
CREATE INDEX WEATHER_TIME_IDX ON WEATHER.WEATHER(time desc);
COMMIT;
