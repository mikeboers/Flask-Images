<!doctype html>
<head>

    <link rel="stylesheet" href="//maxcdn.bootstrapcdn.com/bootstrap/3.2.0/css/bootstrap.min.css">

    <style>

        img {
            border: 1px solid black;
        }

    </style>



<body><div class="container">

    <h1>Flask-Images Demo</h1>

    <p>Flask-Images is a Flask extension that provides dynamic image resizing for your application.

    <form class="form-horizontal" role="form">

        <div class="form-group">
            <label class="control-label" for="url">Source URL:</label>
            <input class="form-control" name="url" size="80" value="{{ url or 'https://farm4.staticflickr.com/3540/5753968652_a28184e5fb.jpg' }}"/>
        </div>

        <div class="form-group">
            <label class="control-label" for="transform">Transform:</label>
            <input class="form-control" name="transform" size="100" value="{{ transform }}" />
        </div>

        <label>Width: <input name="width" size="3" value="{{ width }}" /></label><br/>
        <label>Height: <input name="height" size="3" value="{{ height }}" /></label><br/>
        <label>Background: <input name="background" type="color" size="7" value="{{ background }}" /></label><br/>
        <label>Enlarge: <input name="enlarge" type="checkbox" {{ 'checked' if enlarge else '' }}/></label><br />
        <input type="submit" />
    </form>

    {% if url and (transform or (width and height)) %}
    <p>Results for <strong>{{ url }}:
    <table>
        <tr>
            <td>width={{ width }}
            <td><img src="{{ url_for('images', filename=url,
                transform=transform,
                enlarge=enlarge,
                width=width,
                quality=90,
            ) }}" />
        <tr>
            <td>width={{ width }}<br />height={{ height }}
            <td><img src="{{ url_for('images', filename=url,
                transform=transform,
                enlarge=enlarge,
                width=width,
                height=height,
                quality=90,
            ) }}" />
        <tr>
            <td>width={{ width }}<br />height={{ height }}<br />mode='crop'
            <td><img src="{{ url_for('images.crop', filename=url,
                transform=transform,
                enlarge=enlarge,
                width=width,
                height=height,
                quality=90,
            ) }}" />
        <tr>
            <td>width={{ width }}<br />height={{ height }}<br />mode='fit'
            <td><img src="{{ url_for('images.fit', filename=url,
                transform=transform,
                enlarge=enlarge,
                width=width,
                height=height,
                quality=90,
            ) }}" />
        <tr>
            <td>width={{ width }}<br />height={{ height }}<br />mode='pad'
            <td><img src="{{ url_for('images.pad', filename=url,
                transform=transform,
                enlarge=enlarge,
                width=width,
                height=height,
                background=background,
                quality=90,
            ) }}" />
    {% endif %}
