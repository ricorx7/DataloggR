from flask import Flask, render_template, session, request, copy_current_request_context
from flaskwebgui import FlaskUI
from threading import Lock
from flask_socketio import SocketIO, emit, join_room, leave_room, close_room, rooms, disconnect
from rti_python.Datalogger.DataloggerHardware import DataLoggerHardware

# Set this variable to "threading", "eventlet" or "gevent" to test the
# different async modes, or leave it set to None for the application to choose
# the best option based on installed packages.
async_mode = None

app = Flask(__name__)
ui = FlaskUI(app)
socketio = SocketIO(app, async_mode=async_mode)
thread = None
thread_lock = Lock()

# Datalogger hardward
logger_hardware = DataLoggerHardware()


def background_thread():
    """Example of how to send server generated events to clients."""
    count = 0
    while True:
        socketio.sleep(10)
        count += 1
        socketio.emit('my_response',
                      {'data': 'Server generated event', 'count': count},
                      namespace='/test')


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

@socketio.on('connect', namespace='/test')
def test_connect():
    global thread
    with thread_lock:
        if thread is None:
            thread = socketio.start_background_task(background_thread)
    emit('my_response', {'data': 'Connected', 'count': 0})

@socketio.on('disconnect', namespace='/test')
def test_disconnect():
    print('Client disconnected', request.sid)


# Run the flask APP
ui.run()


if __name__ == '__main__':
    socketio.run(app, debug=True)

