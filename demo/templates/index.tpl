<!doctype html>
<head>
    <style>
        body {
            font-family: Courier, monospace;
            font-size: 12px;
        }
    </style>
<body>
    <p>Welcome to the Flask-Images demo!
    <form action="{{url_for('demo')}}">
        <label for="url">Image URL:</label>
        <input name="url"/>

        <input type="submit" />
    </form>
