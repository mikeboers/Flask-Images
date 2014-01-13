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
    <h1>{{ url }}</h1>
    <table>
        <tr>
            <td>width=200
            <td><img src="{{ url_for('images', filename=url, width=200) }}" />
        <tr>
            <td>width=200<br />height=200
            <td><img src="{{ url_for('images', filename=url, width=200, height=200) }}" />
        <tr>
            <td>width=200<br />height=200<br />mode='crop'
            <td><img src="{{ url_for('images.crop', filename=url, width=200, height=200) }}" />
        <tr>
            <td>width=200<br />height=200<br />mode='fit'
            <td><img src="{{ url_for('images.fit', filename=url, width=200, height=200) }}" />
        <tr>
            <td>width=200<br />height=200<br />mode='pad'
            <td><img src="{{ url_for('images.pad', filename=url, width=200, height=200) }}" />
