from quart import Quart, render_template, jsonify, session, Blueprint, current_app, request
from astropy.io import fits
import asyncio
import asyncpg
import numpy as np
import json
from random import randint
from available_data import get_data

import logging
logging.basicConfig()
log = logging.getLogger('hdltl')

blueprint = Blueprint('transfer_learning', __name__)

@blueprint.route('/transfer_learning')
async def transfer_learning():
    return await render_template('transfer_learning.html', title='Home')


@blueprint.route('/getcutout/<int:slice>/<similarity_type>/')
async def getcutout(slice, similarity_type):

    log.info('getcutout {} {}'.format(slice, similarity_type))

    # Get the data
    data = await get_data(slice)
    width = data['width']
    height = data['height']
    values = data['values']

    # Values we need to pass out
    inds = []
    similarity_values = []

    if similarity_type == 'tsne':

        # Get the tsne value from the database
        async with current_app.pool.acquire() as connection:
            async with connection.transaction():
                row = await connection.fetchrow("""SELECT fingerprint FROM test WHERE fingerprint_type='tsne' and image_id=$1;""", slice)
                tsne_value = json.loads(row['fingerprint'])['values']

    
        query = "SELECT image_id, madlib.dist_norm2(array_agg(e::text::float), '{{{}, {}}}') FROM test, json_array_elements(fingerprint->'values') e WHERE fingerprint_type='tsne' group by 1 order by madlib.dist_norm2(array_agg(e::text::float), '{{{}, {}}}') LIMIT 9;".format(tsne_value[0], tsne_value[1], tsne_value[0], tsne_value[1])
        async with current_app.pool.acquire() as connection:
            async with connection.transaction():
                async for row in connection.cursor(query):
                    inds.append(row[0]) 
                    similarity_values.append(row[1]) 

    elif similarity_type == 'tanimoto':

        # Get the tsne value from the database
        async with current_app.pool.acquire() as connection:
            async with connection.transaction():
                row = await connection.fetchrow("""SELECT fingerprint FROM test WHERE fingerprint_type='tsne' and image_id=$1;""", slice)
                tsne_value = json.loads(row['fingerprint'])['values']

    
        query = "SELECT image_id, madlib.dist_tanimoto(array_agg(e::text::float), '{{{}, {}}}') FROM test, json_array_elements(fingerprint->'values') e WHERE fingerprint_type='tsne' group by 1 order by madlib.dist_tanimoto(array_agg(e::text::float), '{{{}, {}}}') LIMIT 9;".format(tsne_value[0], tsne_value[1], tsne_value[0], tsne_value[1])
        async with current_app.pool.acquire() as connection:
            async with connection.transaction():
                async for row in connection.cursor(query):
                    inds.append(row[0]) 
                    similarity_values.append(row[1]) 


    elif similarity_type == 'norm1':

        # Get the tsne value from the database
        async with current_app.pool.acquire() as connection:
            async with connection.transaction():
                row = await connection.fetchrow("""SELECT fingerprint FROM test WHERE fingerprint_type='tsne' and image_id=$1;""", slice)
                tsne_value = json.loads(row['fingerprint'])['values']

    
        query = "SELECT image_id, dist FROM (select image_id, madlib.dist_norm1(array_agg(e::text::float), '{{{}, {}}}') as dist from test, json_array_elements(fingerprint->'values') e WHERE fingerprint_type='tsne' group by 1 ) a order by dist LIMIT 9;".format(tsne_value[0], tsne_value[1], tsne_value[0], tsne_value[1])
        async with current_app.pool.acquire() as connection:
            async with connection.transaction():
                async for row in connection.cursor(query):
                    inds.append(row[0]) 
                    similarity_values.append(row[1]) 

    elif similarity_type == 'inf_norm':

        # Get the tsne value from the database
        async with current_app.pool.acquire() as connection:
            async with connection.transaction():
                row = await connection.fetchrow("""SELECT fingerprint FROM test WHERE fingerprint_type='tsne' and image_id=$1;""", slice)
                tsne_value = json.loads(row['fingerprint'])['values']

    
        query = "SELECT image_id, dist FROM (select image_id, madlib.dist_inf_norm(array_agg(e::text::float), '{{{}, {}}}') as dist from test, json_array_elements(fingerprint->'values') e WHERE fingerprint_type='tsne' group by 1 ) a order by dist LIMIT 9;".format(tsne_value[0], tsne_value[1], tsne_value[0], tsne_value[1])
        async with current_app.pool.acquire() as connection:
            async with connection.transaction():
                async for row in connection.cursor(query):
                    inds.append(row[0]) 
                    similarity_values.append(row[1]) 

    elif similarity_type == 'cosine_similarity':

        # Get the tsne value from the database
        async with current_app.pool.acquire() as connection:
            async with connection.transaction():
                row = await connection.fetchrow("""SELECT fingerprint FROM test WHERE fingerprint_type='tsne' and image_id=$1;""", slice)
                tsne_value = json.loads(row['fingerprint'])['values']

    
        query = "SELECT image_id, dist FROM (select image_id, madlib.cosine_similarity(array_agg(e::text::float), '{{{}, {}}}') as dist from test, json_array_elements(fingerprint->'values') e WHERE fingerprint_type='tsne' group by 1 ) a order by dist LIMIT 9;".format(tsne_value[0], tsne_value[1], tsne_value[0], tsne_value[1])
        async with current_app.pool.acquire() as connection:
            async with connection.transaction():
                async for row in connection.cursor(query):
                    inds.append(row[0]) 
                    similarity_values.append(row[1]) 

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
                        ORDER BY a.jaccard_dist ASC LIMIT 9;""".format(json.dumps(labels))

        async with current_app.pool.acquire() as connection:
            async with connection.transaction():
                async for row in connection.cursor(query):
                    inds.append(row[0]) 
                    similarity_values.append(row[1]) 


    elif similarity_type == 'none':
        # This is to allow getting of data without having to calculate the information
        pass

    else:
        log.error('Unknown similarity type {}'.format(similarity_type))

    # Create the structure needed by ds3
    data = {
        'rgb': True,
        'width': width,
        'height': height,
        'values': values,
        'similar': (inds[:9], similarity_values)
    }

    return jsonify(data)
