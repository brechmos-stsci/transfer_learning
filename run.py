from quart import Quart
import asyncpg

import logging
logging.basicConfig()
log = logging.getLogger('hdltl')
log.setLevel(logging.INFO)

from hdltl import blueprint as hdltl_blueprint
from available_data import blueprint as available_data_blueprint
from transfer_learning import blueprint as transfer_learning_blueprint

def create_app():
    app = Quart(__name__)
    app.secret_key = '9a8sdyflkhjasdf'
    app.cutouts = None
    app.cutout_similarities = None
    app.cutout_similarities_jaccard = None

    @app.before_first_request
    async def create_db():
        log.info('Initializing the postgres pool')
        app.pool = await asyncpg.create_pool(user='craig', password='dumb', database='hubble', host='127.0.0.1', max_size=20) 

    app.register_blueprint(hdltl_blueprint)
    app.register_blueprint(available_data_blueprint)
    app.register_blueprint(transfer_learning_blueprint)

    return app


if __name__ == '__main__':
    create_app().run()
