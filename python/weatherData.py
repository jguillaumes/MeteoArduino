import datetime as dt
import elasticsearch_dsl as edsl

from elasticsearch import client
from elasticsearch_dsl import connections,DocType,Date,Text,Float

class WeatherData(DocType):
    time = Date(default_timezone='UTC')
    temperature = Float()
    humidity = Float()
    pressure = Float()
    light = Float()
    class Meta:
        suffix = dt.datetime.today().strftime("%Y.%m.%d")
        index = 'weather-1.0.0-' + suffix
    def save(self,** kwargs):
        return super().save(** kwargs)
    def create_template(conn):
        with open('weather-template.json','r') as tempFile:
            template = tempFile.read()
            client.IndicesClient(conn).put_template(name='weather-1.0.0-*',\
                                                body=template)

