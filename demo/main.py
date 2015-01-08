from flask import Flask, request, redirect, render_template
from flask.ext.images import Images


app = Flask(__name__)
app.secret_key = 'monkey'
app.debug = True
images = Images(app)


@app.route('/')
@app.route('/demo')
def index():

    url = request.args.get('url')
    width = max(0, min(1000, int(request.args.get('width', 200))))
    height = max(0, min(1000, int(request.args.get('height', 200))))
    background = request.args.get('background', '#000000')
    transform = request.args.get('transform', '')
    enlarge = bool(request.args.get('enlarge'))
    return render_template('main.tpl',
        url=url,
        width=width,
        height=height,
        background=background,
        transform=transform,
        enlarge=enlarge,
    )


@app.route('/direct/<path:url>')
def direct(url):
    kwargs = {}
    for key in ('width', 'height', 'mode', 'quality', 'transform'):
        value = request.args.get(key) or request.args.get(key[0])
        if value is not None:
            value = int(value) if value.isdigit() else value
            kwargs[key] = value
    return redirect(images.build_url(url, **kwargs))


if __name__ == '__main__':
    app.run(debug=True, use_reloader=True)
