import logging

import redis

from flask import Flask, request, jsonify, abort
from rq import Queue
from rq.job import Job
from rq.exceptions import NoSuchJobError

from service.parser.scraper import parse_messages_data


app = Flask(__name__)

# redis connection
r = redis.Redis(host='redis', port=6379)

# queue object
q = Queue(connection=r)

logging.basicConfig(
    filename='tasks.log',
    level=logging.DEBUG,
    format='%(asctime)s:%(name)s:%(message)s'
)


@app.route('/task', methods=['POST'])
def task():
    """
    Контроллер который создает задание, ставит его в очередь
    и возвращает id задания
    """
    if 'keyword' in request.json:
    # Проверка на наличие keyword в запросе
        keyword = request.json['keyword']
        job = q.enqueue(
            parse_messages_data,
            keyword,
            result_ttl=-1
        )
        logging.debug(f'Added task {job.id} in queue; keyword={keyword}')
        return jsonify({'task_id': job.id})

    else:
        abort(400, 'Bad request! Send keyword as a json')


@app.route('/result', methods=['POST'])
def get_task():
    """
    Контроллер который проверяет статус таска и возвращает
    результат/статус
    """
    try:
        # Проверка на наличие id задания в запросе
        if 'task_id' in request.json:
            task_id = request.json['task_id']
            job = Job.fetch(task_id, connection=r)

            # Проверка статуса задания
            if job.get_status() == "finished":
                logging.debug(f'Result of {job.id} task given away')
                return jsonify({job.id: job.result})
            
            else:
                status = job.get_status()
                logging.debug(
                    f'Requested result of {job.id}. Task in {status} status'
                )
                return jsonify({'task_status': status})

        else:
            abort(400, 'Bad request! Send task_id as a json')

    # Исключение когда введен неверный номер таска
    except NoSuchJobError:
        abort(404, 'No such task!')


if __name__ == "__main__":
    app.run()
