from flask import Flask, request
from flask import render_template
from flaskwebgui import FlaskUI

# RUN THE APP
# Windows
# set FLASK_APP=flask_webserver.py
# flask run
#
# Linux
# export FLASK_APP=flask_webserver.py
# flask run

app = Flask(__name__)
ui = FlaskUI(app)


@app.route("/")
def main_page():

    comm_port_list = ["COM3", "COMM4"]
    return render_template("download.j2", comm_ports=comm_port_list)


@app.route("/download")
def download_page(selected_comm: str):
    comm_port_list = ["COM3", "COMM4"]
    print("Selected Port: " + selected_comm)
    # Remove the duplicate selected comm port
    if selected_comm in comm_port_list:
        comm_port_list.remove(selected_comm)

    return render_template("download.j2", comm_ports=comm_port_list, selected_comm_port=selected_comm)


@app.route("/serial_connect", methods=['POST'])
def serial_connect():
    selected_comm_port = request.form.get('comm_port_select')
    print(selected_comm_port)
    return download_page(selected_comm_port)


# Run the flask APP
ui.run()

