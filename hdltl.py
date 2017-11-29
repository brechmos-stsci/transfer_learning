from quart import render_template, Blueprint

blueprint = Blueprint('index', __name__)

@blueprint.route('/')
@blueprint.route('/index')
async def index():
    return await render_template('index.html', title='Home')

