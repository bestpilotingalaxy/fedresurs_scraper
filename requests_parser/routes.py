import redis
from flask import Flask, request, jsonify
from rq import Queue
from rq.job import Job
import time

from .parser import parse_messages_data


app = Flask(__name__)
r = redis.Redis()
q = Queue(connection=r)


@app.route('/task', methods=['POST'])
def task():
    if 'keyword' in request.json:
        keyword = request.json['keyword']
        job = q.enqueue(
            parse_messages_data,
            keyword,
            result_ttl=-1
        )
        return jsonify({'task_id': job.id})
    else:
        return 'Send keyword for parsing as a json!'


@app.route('/result', methods=['POST'])
def get_task():
    if 'task_id' in request.json:
        task_id = request.json['task_id']
        job = Job.fetch(task_id, connection=r)
        if job.get_status() == "finished":
            return jsonify({job.id: job.result})
        else:
            return job.get_status()
    else:
        return 'Send task_id as a json'


if __name__ == "__main__":
    app.run()
