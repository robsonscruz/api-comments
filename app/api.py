from flask import Flask, request, Response, jsonify
from json import dumps, loads
from middleware import set_unhealth, set_unready_for_seconds, middleware
import os 
from pymongo import MongoClient
from marshmallow import Schema, fields, ValidationError
import subprocess
from prometheus_flask_exporter import PrometheusMetrics

app = Flask('comentarios')
app.wsgi_app = middleware(app.wsgi_app)
metrics = PrometheusMetrics(app, default_labels={'version': '1.0'})

app.debug = True

# DB
app.config['ENV']         = os.getenv("ENV", "dev")
app.config['MONGODB_URL'] = os.getenv("MONGODB_URL", "mongodb+srv://localhost:27017/db_commets?retryWrites=true&w=majority")
app.config['MONGODB_DB']  = os.getenv("MONGODB_DB", "xpto_database")
app.config['VERSION_APP'] = os.getenv("VERSION_APP", "v.1.0.0")
client = MongoClient(app.config['MONGODB_URL'])
db = client[app.config['MONGODB_DB']]

# Schema
class CommentsSchema(Schema):
    email       = fields.String(required=True)
    comment     = fields.String(required=True)
    content_id  = fields.Integer(required=True)

@app.route('/')
def index():
    return jsonify({'api': app.config['VERSION_APP'], 'host': os.uname().nodename, 'env': app.config['ENV']})

@app.route('/unhealth', methods=['PUT'])
def unhealth():
    set_unhealth()
    return Response('OK')

@app.route('/unreadyfor/<int:seconds>', methods=['PUT'])
def unready_for(seconds):
    set_unready_for_seconds(seconds)
    return Response('OK')

@app.route('/health', methods=['GET'])
def heath():
    return Response('OK')

@app.route('/ready', methods=['GET'])
def ready():
    return Response('OK')

@app.route('/stress/<int:seconds>')
def stress(seconds):
    # run stress
    process = subprocess.Popen("stress-ng -c 64 -t {}".format(seconds), shell=True, stdout=subprocess.PIPE)
    process.wait()
    return Response('OK')

@app.route('/api/comment/new', methods=['POST'])
def api_comment_new():
    request_data = request.get_json()
    schema = CommentsSchema()
    try:
        # Validate request body against schema data types
        result = schema.load(request_data)
        # Save new comment
        db.commets.insert_one(request_data)
    except ValidationError as err:
        # Return a nice message if validation fails
        return jsonify(err.messages), 400

    message = 'comment created and associated with content_id {}'.format(request_data['content_id'])

    # Send data back as JSON
    return jsonify({'status': 'SUCCESS', 'message': message }), 200

@app.route('/api/comment/list/<content_id>')
def api_comment_list(content_id):
    if content_id is not None and content_id.isnumeric():
        content_id = int(content_id)

    if not isinstance(content_id, int):
        return jsonify({'status': 'INVALID-PARAMETER', 'message': 'content_id {} is invalid.'.format(content_id)}), 400

    # Find DB
    comments = list(db.commets.find({"content_id" : content_id}, {"email":1, "comment": 1, "content_id": 1, "_id": 0}))

    if not comments:
        return jsonify({'status': 'NOT-FOUND', 'message': 'content_id {} not found'.format(content_id)}), 404

    return jsonify(comments), 200

if __name__ == '__main__':
    app.run()
