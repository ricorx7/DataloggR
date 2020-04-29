from flask import Flask, request
from flask import render_template
from flaskwebgui import FlaskUI
from rti_python.Datalogger.DataloggerHardware import DataLoggerHardware

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

# Datalogger hardward
logger_hardware = DataLoggerHardware()


@app.route("/")
def main_page():
    # Use Download page as main
    return download_page(None, None)


@app.route("/download")
def download_page(selected_comm: str, selected_baud: str):
    comm_port_list = logger_hardware.get_serial_ports()
    baud_list = logger_hardware.get_baud_rates()
    if selected_comm:
        print("Selected Port: " + selected_comm)
    if selected_baud:
        print("Selected Port: " + selected_baud)

    # Remove the duplicate selected comm port
    if selected_comm in comm_port_list:
        comm_port_list.remove(selected_comm)
    if selected_baud in baud_list:
        baud_list.remove(selected_baud)

    return render_template("download.j2", comm_ports=comm_port_list, bauds=baud_list, selected_comm_port=selected_comm, selected_baud=selected_baud)


@app.route("/serial_connect", methods=['POST'])
def serial_connect():
    selected_comm_port = request.form.get('comm_port_selected')
    selected_baud = request.form.get('baud_selected')
    print(selected_comm_port)
    print(selected_baud)
    return download_page(selected_comm_port, selected_baud)


@app.route("/scan_serial", methods=['POST'])
def scan_serial():
    selected_comm_port = request.form.get('comm_port_selected')
    selected_baud = request.form.get('baud_selected')
    print(selected_comm_port)
    print(selected_baud)
    return download_page(selected_comm_port, selected_baud)


# Run the flask APP
ui.run()

