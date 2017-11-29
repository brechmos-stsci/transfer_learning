from quart import Quart, render_template, jsonify, session, Blueprint, current_app, request
from astropy.io import fits
import asyncio
import asyncpg
import numpy as np
import json
from random import randint

blueprint = Blueprint('available_data', __name__)

@blueprint.route('/data/<int:id>/')
async def get_data(id):

    to_send = np.zeros((224,224,4))
    to_send[:,:,:3] = np.load('data/image_{}.npy'.format(id))

    # rescale to be between 0 and 255
    cmin, cmax = np.percentile(to_send, [3, 97])
    to_send = np.clip((to_send - cmin) / (cmax-cmin) * 255, 0, 255)
    to_send[:,:,3] = 255*np.ones((224,224))

    data = {
        'rgb': True,
        'width': to_send.shape[0], 
        'height': to_send.shape[1], 
        'values': to_send.transpose((2,0,1)).ravel(order='F').tolist(),
    }

    return jsonify(data)
