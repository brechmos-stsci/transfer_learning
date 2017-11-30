from quart import Blueprint
import numpy as np

import logging
logging.basicConfig()
log = logging.getLogger('hdltl')

blueprint = Blueprint('available_data', __name__)


@blueprint.route('/data/<int:id>/')
async def get_data(data_id):

    log.info('Getting data for id {}'.format(data_id))

    # rgb + alpha channel
    data = np.load('data/carina/image_{}.npy'.format(data_id))

    # rescale to be between 0 and 255
    to_send = normalize_rgb(data, 3, 97)

    return {
        'rgb': True,
        'width': to_send.shape[0], 
        'height': to_send.shape[1], 
        'values': to_send.transpose((2, 0, 1)).ravel(order='F').tolist(),
    }


def normalize_rgb(data, lower_percentile=3, upper_percentile=97):
    """
    Normalize the RGB data to be between 0 and 255 and also add 
    an alpha channel 
    """

    nrows, ncols = data.shape[:2]

    data_out = np.zeros((nrows, ncols, 4))

    # rescale to be between 0 and 255
    cmin, cmax = np.percentile(data, [lower_percentile, upper_percentile])
    data_out[:, :, :3] = np.clip((data - cmin) / (cmax-cmin) * 255, 0, 255)

    # Add Alpha channel
    data_out[:, :, 3] = 255*np.ones((nrows, ncols))

    return data_out
