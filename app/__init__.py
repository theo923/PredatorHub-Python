from flask import Flask
from flask_cors import CORS
from flask_restx import Api, Resource, fields
from flask_mysqldb import MySQL
from app.utils.getFavicon import getFavicon
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


def init_app():
    app = Flask(__name__)
    CORS(app)
    api = Api(app)

    MYSQL_HOST = os.getenv('MYSQL_HOST')
    MYSQL_PORT = int(os.getenv('MYSQL_PORT'))
    MYSQL_USER = os.getenv('MYSQL_USER')
    MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD')
    MYSQL_DB = os.getenv('MYSQL_DB')
    MYSQL_DATABASE_CHARSET = os.getenv('MYSQL_DATABASE_CHARSET')

    app.config['MYSQL_HOST'] = MYSQL_HOST
    app.config['MYSQL_PORT'] = MYSQL_PORT
    app.config['MYSQL_USER'] = MYSQL_USER
    app.config['MYSQL_PASSWORD'] = MYSQL_PASSWORD
    app.config['MYSQL_DB'] = MYSQL_DB
    app.config['MYSQL_DATABASE_CHARSET'] = MYSQL_DATABASE_CHARSET

    mysql = MySQL(app)

    def create_table():
        cur = mysql.connection.cursor()
        cur.execute('''
            CREATE TABLE IF NOT EXISTS bookmarks (
                id INT PRIMARY KEY AUTO_INCREMENT,
                url VARCHAR(255) NOT NULL,
                name VARCHAR(255) NOT NULL,
                favicon_url VARCHAR(255) NOT NULL
            )
        ''')
        mysql.connection.commit()
        cur.close()

    with app.app_context():
        create_table()

    url_model = api.model('URL', {
        'url': fields.String(required=True,
                             description='The URL to fetch the favicon from.'),
        'name': fields.String(required=True,
                              description='The name of the bookmark.')
    })

    @api.route('/bookmarks')
    class BookmarkResource(Resource):
        @api.expect(url_model, validate=True)
        def post(self):
            data = api.payload
            url = data['url']
            name = data['name']
            favicon_url = getFavicon(url)

            # Save the bookmark in the database
            cur = mysql.connection.cursor()
            cur.execute(
                'INSERT INTO bookmarks (url, name, favicon_url)\
                      VALUES (%s, %s, %s)',
                (url, name, favicon_url)
            )
            mysql.connection.commit()
            cur.close()

            return {'message': 'Bookmark saved successfully.'}

        def get(self):
            cur = mysql.connection.cursor()
            cur.execute('SELECT * FROM bookmarks')
            bookmarks = cur.fetchall()
            cur.close()

            result = []
            for bookmark in bookmarks:
                bookmark_data = {
                    'id': bookmark[0],
                    'url': bookmark[1],
                    'name': bookmark[2],
                    'favicon_url': bookmark[3]
                }
                result.append(bookmark_data)

            return {'bookmarks': result}

    @app.route('/')
    def Hello():
        return 'Hello World!'

    @app.route('/health')
    def health():
        return 'OK'

    return app
