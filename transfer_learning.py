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

import transfer_learning_queries as tlqueries

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


    if similarity_type in ['tsne', 'tanimoto', 'norm1', 'inf_norm', 'cosine_similarity']:

        # Get the query
        query = tlqueries.queries[similarity_type]

        # Get the tsne value for the main image from the database
        async with current_app.pool.acquire() as connection:
            async with connection.transaction():
                row = await connection.fetchrow("""SELECT fingerprint FROM test WHERE fingerprint_type='tsne' and image_id=$1;""", slice)
                tsne_value = json.loads(row['fingerprint'])['values']

    
        # Find the similar images
        query = query.format(tsne_value[0], tsne_value[1])
        async with current_app.pool.acquire() as connection:
            async with connection.transaction():
                async for row in connection.cursor(query):
                    inds.append(row[0]) 
                    similarity_values.append(row[1]) 



    elif similarity_type == 'jaccard':

        # Get the query
        query = tlqueries.queries[similarity_type]

        # Get the fingerprint for the main image from the database
        async with current_app.pool.acquire() as connection:
            async with connection.transaction():
                # Get the tsne value from the database
                row = await connection.fetchrow("""SELECT fingerprint FROM test WHERE fingerprint_type='fingerprints' and image_id={};""".format(slice))
                labels = json.loads(row[0])['labels']
        
        query = query.format(json.dumps(labels))

        # Find the similar images
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
