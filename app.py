from flask import Flask, render_template, session, request, copy_current_request_context, flash, redirect, jsonify
from flaskwebgui import FlaskUI
from threading import Lock
from flask_socketio import SocketIO, emit, join_room, leave_room, close_room, rooms, disconnect
from forms import SerialPortForm
import json
import rti_python.Datalogger.DataloggerHardware as data_logger
from tkinter import filedialog
from tkinter import *

# Set this variable to "threading", "eventlet" or "gevent" to test the
# different async modes, or leave it set to None for the application to choose
# the best option based on installed packages.
async_mode = None

app = Flask(__name__)
app.config['SECRET_KEY'] = 'you-will-never-guess'
ui = FlaskUI(app)
socketio = SocketIO(app, async_mode=async_mode)
thread = None
thread_lock = Lock()

# Datalogger hardware
logger_hardware = data_logger.DataLoggerHardware()

# Socket IO 
count = 0

# Current serial port
selected_serial_port = None
selected_baud_rate = None


def background_thread():
    """Example of how to send server generated events to clients."""
    count = 0
    while True:
        socketio.sleep(10)
        count += 1
        socketio.emit('status_report',
                      {'data': 'Server generated event', 'count': count},
                      namespace='/test')


        dl_status = logger_hardware.get_status()
        #json_dl_status = jsonify(dl_status)
        json_dl_status = json.dumps(dl_status)
        socketio.emit('dl_status',
                        json_dl_status,
                        namespace='/test')



@app.route("/")
def main_page():
    # Use Download page as main
    #return download_page(None, None)
    #return redirect('/serial')
    #return serial_page(None, None)
    form = SerialPortForm()
    return render_template('serial.j2', form=form)


@app.route('/serial_scan', methods=['POST'])
def serial_scan():
    print("Scan Serial Ports")

    socketio.emit('status_report',
                {'data': 'Scan Serial Ports', 'count': count},
                namespace='/test')

    return jsonify(data={'port_list': data_logger.get_serial_ports()})


@app.route('/browse_folder', methods=['POST'])
def browse_folder():
    print("Browse for Folder")

    folder_path = logger_hardware.browse_folder()

    dl_status = logger_hardware.get_status()
    #json_dl_status = jsonify(dl_status)
    json_dl_status = json.dumps(dl_status)
    socketio.emit('dl_status',
                    json_dl_status,
                    namespace='/test')

    return jsonify(data={'folder_path': folder_path})


@app.route('/serial_connect', methods=['POST'])
def serial_connect():
    form = SerialPortForm()
    print("CALL Serial Connect")
    if form.validate_on_submit():
        print("SERIAL Connect")

        # Try to connect to the serial port
        connect_status = logger_hardware.connect_serial(form.comm_port.data, int(form.baud_rate.data))

        return jsonify(data={
                                'comm_port': '{}'.format(form.comm_port.data),
                                'baud_rate': '{}'.format(form.baud_rate.data),
                                'Status': connect_status
                                })
    
    # If not valid, return errors
    return jsonify(data=form.errors)


@app.route('/serial_disconnect', methods=['POST'])
def serial_disconnect():
    form = SerialPortForm()
    print("CALL Serial Disconnect")
    if form.validate_on_submit():
        print("SERIAL Disconnect")

        # Try to connect to the serial port
        connect_status = "Disconnect"
        logger_hardware.disconnect_serial()

        return jsonify(data={
                                'comm_port': '{}'.format(form.comm_port.data),
                                'baud_rate': '{}'.format(form.baud_rate.data),
                                'Status': '{}'.format(connect_status)
                                })
    
    # If not valid, return errors
    return jsonify(data=form.errors)


@app.route('/download', methods=['POST'])
def download():
    print("CALL Download")

    # Start the download process
    logger_hardware.download()

    return jsonify(data={
        'status': 'Downloading'
    })

    # If not valid, return errors
    return jsonify(data=form.errors)

"""
@app.route("/serial", methods=['GET', 'POST'])
#def serial_page(selected_port: str = None, selected_baud: str = None):
def serial_page():
    # Global values to keep track of selected items
    global selected_serial_port
    global selected_baud_rate

    # Create the form
    serial_port_form = SerialPortForm()

    # Set the selected values if previously set
    serial_port_form.comm_port.choices = data_logger.get_serial_ports_tuple()
    if selected_serial_port:
        serial_port_form.comm_port.default = selected_serial_port
    if selected_baud_rate:
        serial_port_form.baud_rate.default = selected_baud_rate

    # Check for POST
    if serial_port_form.validate_on_submit():
        flash('COMM Port {}, Baud Rate={}'.format(serial_port_form.comm_port.data, serial_port_form.baud_rate.data))
        selected_serial_port = serial_port_form.comm_port.data
        selected_baud_rate = serial_port_form.baud_rate.data
        if serial_port_form.scan.data:
            flash("SCAN New Ports")
        if serial_port_form.connect.data:
            flash("Connect ADCP Serial Port")
        if serial_port_form.disconnect.data:
            flash("Disconnect ADCP Serial Port")
        print("Scan Value : {value}".format(value=serial_port_form.scan.data))
        print("Connect Value : {value}".format(value=serial_port_form.connect.data))
        print("Disconnect Value : {value}".format(value=serial_port_form.disconnect.data))
        return redirect('/serial')
        #return serial_page(serial_port_form.comm_port.data, serial_port_form.baud_rate.data)

    # Check for errors
    if serial_port_form.errors:
        print("***ERROR with SerialPort Page***")
        for error in serial_port_form.errors:
            print(error)

    # GET
    return render_template('serialport.j2', title='Serial Port', form=serial_port_form)


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

    return render_template("download.j2", comm_ports=comm_port_list, bauds=baud_list, selected_comm_port=selected_comm, selected_baud=selected_baud, async_mode=socketio.async_mode)


@app.route("/scan_serial", methods=['POST'])
def scan_serial():
    selected_comm_port = request.form.get('comm_port_selected')
    selected_baud = request.form.get('baud_selected')
    print(selected_comm_port)
    print(selected_baud)
    return download_page(selected_comm_port, selected_baud)

@socketio.on('connect_serial', namespace='/test')
def serial_connect(message):
    print("CONNECT SERIAL PORT")
    emit('my_response', {'data': message['data']})

@socketio.on('disconnect_serial', namespace='/test')
def serial_disconnect(message):
    print("DISCONNECT SERIAL PORT")
    emit('my_response', {'data': message['data']})


@socketio.on('my event', namespace='/test')
def test_message(message):
    emit('my_response', {'data': message['data']})

@socketio.on('my broadcast event', namespace='/test')
def test_broad_message(message):
    emit('my_response', {'data': message['data']}, broadcast=True)
"""

@socketio.on('connect', namespace='/test')
def test_connect():
    global thread
    with thread_lock:
        if thread is None:
            @copy_current_request_context
            def ctx_bridge():
                background_thread()


            thread = socketio.start_background_task(ctx_bridge)
    emit('status_report', {'data': 'Connected', 'count': 0})

@socketio.on('disconnect', namespace='/test')
def test_disconnect():
    print('Client disconnected', request.sid)


# Run the flask APP
ui.run()


if __name__ == '__main__':
    socketio.run(app, debug=True)

