from quart import Quart, render_template, jsonify, session, Blueprint, current_app, request
from astropy.io import fits
import asyncio
import asyncpg
import numpy as np
import json
from random import randint
import psycopg2

hello_blueprint = Blueprint('hello', __name__)

@hello_blueprint.route('/')
@hello_blueprint.route('/index')
async def index():
    return await render_template('index.html', title='Home')


@hello_blueprint.route('/getcutout/<slice>/<similarity_type>/')
async def getcutout(slice, similarity_type):

    print('getcutout {} {}'.format(slice, similarity_type))

    # Comes in as ae string, so convert to int
    slice = int(slice)

    to_send = np.zeros((224,224,4))
    to_send[:,:,:3] = np.load('data/image_{}.npy'.format(slice))

    # rescale to be between 0 and 255
    cmin, cmax = np.percentile(to_send, [3, 97])
    to_send = np.clip((to_send - cmin) / (cmax-cmin) * 255, 0, 255)
    to_send[:,:,3] = 255*np.ones((224,224))

    if similarity_type == 'tsne':

        # Get the tsne value from the database
        async with current_app.pool.acquire() as connection:
            async with connection.transaction():
                row = await connection.fetchrow("""SELECT fingerprint FROM test WHERE fingerprint_type='tsne' and image_id=$1;""", slice)
                tsne_value = json.loads(row['fingerprint'])['values']

    
        query = "SELECT image_id, madlib.dist_norm2(array_agg(e::text::float), '{{{}, {}}}') FROM test, json_array_elements(fingerprint->'values') e WHERE fingerprint_type='tsne' group by 1 order by madlib.dist_norm2(array_agg(e::text::float), '{{{}, {}}}');".format(tsne_value[0], tsne_value[1], tsne_value[0], tsne_value[1])
        async with current_app.pool.acquire() as connection:
            async with connection.transaction():
                count = 0
                inds = []
                similarity_values = []
                async for row in connection.cursor(query):
                    inds.append(row[0]) 
                    similarity_values.append(row[1]) 
                    if count > 9:
                        break
                    else:
                        count = count + 1

    elif similarity_type == 'jaccard':

        async with current_app.pool.acquire() as connection:
            async with connection.transaction():
                # Get the tsne value from the database
                row = await connection.fetchrow("""SELECT fingerprint FROM test WHERE fingerprint_type='fingerprints' and image_id={};""".format(slice))
                labels = json.loads(row[0])['labels']
        
        query = """ select a.image_id, 
                           a.jaccard_dist from ( 
                               select image_id, 
                                      ( 1.0 - ( 
                                         (select count(*) from ( select unnest(array_agg(e::text)) intersect  select unnest(array_agg(f::text)) ) a )::decimal / 
                                          array_length(array_union(array_agg(e::text), array_agg(f::text)), 1)::decimal ) )::float
                                      as jaccard_dist 
                               from test, 
                                    json_array_elements(fingerprint->'labels') e, 
                                    json_array_elements('{}') f group by 1 
                            ) a  
                        ORDER BY a.jaccard_dist ASC LIMIT 10;""".format(json.dumps(labels))

        async with current_app.pool.acquire() as connection:
            async with connection.transaction():
                count = 0
                inds = []
                similarity_values = []
                async for row in connection.cursor(query):

                    print(row)
                    inds.append(row[0]) 
                    similarity_values.append(row[1]) 

                    if count > 9:
                        break
                    else:
                        count = count + 1

    else:
        inds = []
        similarity_values = []

    # Create the structure needed by ds3
    data = {
        'rgb': True,
        'width': to_send.shape[0], 
        'height': to_send.shape[1], 
        'values': to_send.transpose((2,0,1)).ravel(order='F').tolist(),
        'similar': (inds[:9], similarity_values)
    }

    return jsonify(data)

def create_app():
    print('in create_app')
    app = Quart(__name__)
    app.secret_key = '9a8sdyflkhjasdf'
    app.cutouts = None
    app.cutout_similarities = None
    app.cutout_similarities_jaccard = None

    @app.before_first_request
    async def create_db():
        print('initializing the pool')
        app.pool = await asyncpg.create_pool(user='craig', password='dumb', database='hubble', host='127.0.0.1', max_size=20) 

    app.register_blueprint(hello_blueprint)

    return app


if __name__ == '__main__':
    create_app().run()
