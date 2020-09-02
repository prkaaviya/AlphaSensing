from flask import Flask, request
from flask_restful import Resource, Api

app = Flask(__name__)
api = Api(app)


class Home(Resource):
    def get(self):
        return {
            'message' : 'OK'
        }


class About(Resource):
    def get(self):
        return {
            'GIS End' : 'GeoJson'
        }

    def post(self):
        data = request.get_json()
        return {
            'message' : data
        }


class Multi(Resource):
    def get(self, num):
        return {
            'GIS End' : num*10
        }


api.add_resource(Home, '/')
api.add_resource(About, '/about')
api.add_resource(Multi, '/multi<int:num>')

if __name__ == '__main__' :
    app.run(debug=True)

