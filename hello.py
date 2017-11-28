from flask import Flask, render_template, jsonify, session
from astropy.io import fits
import numpy as np
from random import randint
app = Flask(__name__)
app.secret_key = '9a8sdyflkhjasdf'
app.cutouts = None
app.cutout_similarities = None
app.cutout_similarities_jaccard = None

@app.route('/')
@app.route('/index')
def index():
    return render_template('loading.html',
                           title='Home')


@app.route('/main/')
def main():
    user = {'nickname': 'fred'}  # fake user

    return render_template('index.html',
                           title='Home',
                           user=user)


@app.route('/getimage/<slice>/')
def getimage(slice):

    # Comes in as a string, so convert to int
    slice = int(slice)

    # Load the data
    f = fits.open('all_g235h-f170lp_s3d_fixed.fits')
    data = f[1].data 

    # Create the structure needed by ds3
    data = {
        'rgb': False,
        'width': data[10].shape[0], 
        'height': data[10].shape[1], 
        'values': data[slice].ravel().tolist()
    }

    return jsonify(data)

@app.route('/load/')
def load():

    if not hasattr(app, 'cutouts') or app.cutouts is None:
        session['number'] = randint(0,999)
        
        print('Loading cutouts')
        app.cutouts = np.load('carina_224.npy')#, mmap_mode='r')
        app.cutouts = app.cutouts.astype(np.float16)
        
        print('Loading similarities')
        app.cutout_similarities = np.load('carina_tsne_coords.npy')

        print('Loading Jaccard similarityies')
        app.cutout_similarities_jaccard = np.load('carina_jaccard.npy')

        print('Done loading')
    return jsonify('ok')



@app.route('/getcutout/<slice>/<similarity_type>/')
def getcutout(slice, similarity_type):

    #if not hasattr(app, 'cutouts') or app.cutouts is None:
        #session['number'] = randint(0,999)
        #app.cutouts = np.load('carina_224.npy')#, mmap_mode='r')
        #app.cutouts = app.cutouts.astype(np.float16)
        
        #app.cutout_similarities = np.load('carina_tsne_coords.npy')
        #app.cutout_similarities_jaccard = np.load('carina_jaccard.npy')

    # Comes in as ae string, so convert to int
    slice = int(slice)

    to_send = np.zeros((224,224,4))
    to_send[:,:,:3] = app.cutouts[:,:,:,slice]

    # rescale to be between 0 and 255
    cmin, cmax = np.percentile(to_send, [3, 97])
    to_send = np.clip((to_send - cmin) / (cmax-cmin) * 255, 0, 255)
    to_send[:,:,3] = 255*np.ones((224,224))

    # Find the 9 similar images
    if similarity_type == 'tsne':
        similarity_values = np.sqrt(np.sum((app.cutout_similarities - np.tile(app.cutout_similarities[slice], (app.cutout_similarities.shape[0],1)))**2,axis=1))
        inds = np.argsort(similarity_values)
        similarity_values = similarity_values[inds]
    elif similarity_type == 'jaccard':
        inds = np.argsort(app.cutout_similarities_jaccard[slice])[::-1]
        similarity_values = app.cutout_similarities_jaccard[slice][inds]
    else:
        raise Exception('bad similarity_type')


    # Create the structure needed by ds3
    data = {
        'rgb': True,
        'width': app.cutouts.shape[0], 
        'height': app.cutouts.shape[1], 
        'values': to_send.transpose((2,0,1)).ravel(order='F').tolist(),
        'similar': (inds[:9].tolist(), similarity_values.tolist())
    }

    return jsonify(data)
