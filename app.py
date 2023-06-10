from flask import Flask
from flask_cors import CORS
from flask_restx import Api, Resource, fields
from app.endpoints.getFavicon import getFavicon
app = Flask(__name__)
CORS(app)
api = Api(app)

url_model = api.model('URL', {'url': fields.String(
    required=True, description='The URL to fetch the favicon from.')})


@app.route('/')
def Hello():
    return 'Hello World!'


@api.route('/favicon')
class FaviconResource(Resource):
    @api.expect(url_model, validate=True)
    def post(self):
        url = api.payload['url']
        favicon_url = getFavicon(url)
        return {'favicon_url': favicon_url}


if __name__ == '__main__':
    app.run(debug=True)
