<!doctype html>
<head>
    <style>
        body {
            font-family: Courier, monospace;
            font-size: 12px;
        }
        h1 {
            font-size 1.5em;
        }
        td {
            vertical-align: top;
        }
        img {
            border: 1px solid black;
        }
    </style>
<body>
    <p>Welcome to the Flask-Images demo!
    <form>

        <label>Source URL:
            <input name="url" size="80" value="{{ url or 'https://farm4.staticflickr.com/3540/5753968652_a28184e5fb.jpg' }}"/>
        </label><br/>
        <label>Width: <input name="width" size="3" value="{{ width }}" /></label><br/>
        <label>Height: <input name="height" size="3" value="{{ height }}" /></label><br/>
        <label>Background: <input name="background" size="7" value="{{ background }}" /></label><br/>

        <input type="submit" />
    </form>

    {% if url and width and height %}
    <p>Results for <strong>{{ url }}:
    <table>
        <tr>
            <td>width={{ width }}
            <td><img src="{{ url_for('images', filename=url, width=width) }}" />
        <tr>
            <td>width={{ width }}<br />height={{ height }}
            <td><img src="{{ url_for('images', filename=url, width=width, height=height) }}" />
        <tr>
            <td>width={{ width }}<br />height={{ height }}<br />mode='crop'
            <td><img src="{{ url_for('images.crop', filename=url, width=width, height=height) }}" />
        <tr>
            <td>width={{ width }}<br />height={{ height }}<br />mode='fit'
            <td><img src="{{ url_for('images.fit', filename=url, width=width, height=height) }}" />
        <tr>
            <td>width={{ width }}<br />height={{ height }}<br />mode='pad'
            <td><img src="{{ url_for('images.pad', filename=url, width=width, height=height, background=background) }}" />
    {% endif %}
