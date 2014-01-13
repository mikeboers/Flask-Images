from flask import Flask, request, redirect
from flask.ext.images import Images


app = Flask(__name__)
app.secret_key = 'monkey'
images = Images(app)


@app.route('/')
def do_main():
    return '''Welcome to the Flask-Images demo!''', 200, [('Content-Type', 'text/plain')]

@app.route('/<path:url>')
def do_url(url):
    kwargs = {}
    for key in ('width', 'height', 'mode', 'quality'):
        value = request.args.get(key) or request.args.get(key[0])
        if value is not None:
            value = int(value) if value.isdigit() else value
            kwargs[key] = value
    return redirect(images.build_url(url, **kwargs))


if __name__ == '__main__':
    app.run(debug=True, use_reloader=True)
