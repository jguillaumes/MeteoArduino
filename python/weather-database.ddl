CREATE TABLE WEATHER (tsa bigint primary key, time timestamp, temperature real, humidity real, pressure real, light real);
CREATE INDEX WEATHER_TIME_IDX ON WEATHER(time desc);
COMMIT;
