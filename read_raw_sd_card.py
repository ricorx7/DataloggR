import os, string
from pathlib import Path
import sys, traceback, types
from rti_python.Codecs.AdcpCodec import AdcpCodec
import time
import humanize

TIMEOUT_START = 10

# Init time
t0 = time.process_time()
ens_count = 0
timeout = TIMEOUT_START

def is_user_admin():

    if os.name == 'nt':
        import ctypes
        # WARNING: requires Windows XP SP2 or higher!
        try:
            return ctypes.windll.shell32.IsUserAnAdmin()
        except:
            traceback.print_exc()
            print("Admin check failed, assuming not an admin.")
            return False
    elif os.name == 'posix':
        # Check for root on Posix
        return os.getuid() == 0
    else:
        raise(RuntimeError, "Unsupported operating system for this module: %s" % (os.name,))


def get_drive_list():
    """
    list all the drive.  Also list available drive.
    :return:
    """
    available_drives = ['%s:' % d for d in string.ascii_uppercase if os.path.exists('%s:' % d)]
    print("Available Drives: " + str(available_drives))

    all_drives = os.popen("fsutil fsinfo drives").readlines()
    print("All Drive: " + all_drives[1])


def read_drive(drive: str):
    global timeout

    BUFFER_SIZE = 1024*512*1
    byte_count = 0

    try:
        path = Path(drive)

        # Verify path exist
        if path.exists() and path.is_dir():
            print(drive + " exists.")
        else:
            print(drive + " does not exist.")

        """
        # Open drive
        #with path.open('rb') as disk:
        """

        # Decode the data
        codec = AdcpCodec()
        codec.ensemble_event += ensemble_rcv

        # Get the start time
        t0 = time.process_time()

        # This must be run as ADMIN
        with open(r"\\.\H:", 'rb') as disk:
            while True:
                # Read the data
                # Use a large buffer size

                data = disk.read(BUFFER_SIZE)
                byte_count = byte_count + BUFFER_SIZE
                print("Read Buffer")

                # Add data to the codec
                codec.add(data)
                print("Codec Buffer Size: " + humanize.naturalsize(codec.binary_codec.buffer_size()))
                print("Bytes Read: " + humanize.naturalsize(byte_count))
                print("Timeout: " + str(timeout))
                print("Total Size: " + humanize.naturalsize(byte_count))
                print("Total Ensembles: " + str(ens_count))

                # Check if there is no more data
                if data == 0:
                    break

                # Check for timeout
                timeout = timeout - 1
                if timeout == 0:
                    break

                # Allow processing
                #time.sleep(1)

            # Data Processing Complete
            print("Data Processing Complete")

            # Shutdown the codec
            codec.shutdown()

    except Exception as ex:
        print("Error reading drive.  " + drive)
        print(ex)
        codec.shutdown()

    t1 = time.process_time()
    print("Time Start: " + humanize.naturaltime(t0))
    print("Time End:   " + humanize.naturaltime(t1))
    print("Elapsed Time: " + humanize.naturaltime(t1-t0))


def ensemble_rcv(sender, ens):
    global ens_count
    global timeout

    t1 = time.process_time()

    # Keep track of ensemble
    ens_count = ens_count + 1

    # Print every 100
    if ens_count % 100 == 0:
        if ens.IsEnsembleData:
            print("Ensemble Received: " + str(ens_count) + " " + str(ens.EnsembleData.EnsembleNumber) + " " + humanize.naturaltime(t0) + " " + humanize.naturaltime(t1) + " " + humanize.naturaltime(t1-t0))
        else:
            print("Ensemble Received: " + str(ens_count) + " " + humanize.naturaltime(t0) + " " + humanize.naturaltime(t1) + " " + humanize.naturaltime(t1-t0))

    # Reset timeout
    timeout = TIMEOUT_START

def run_as_admin(cmd_line=None, wait=True):
    """
    If the application is not running as ADMIN, this will start the
    application as ADMIN mode.
    :param cmd_line:
    :param wait:
    :return:
    """
    if os.name != 'nt':
        raise(RuntimeError, "This function is only implemented on Windows.")

    import win32api, win32con, win32event, win32process
    from win32com.shell.shell import ShellExecuteEx
    from win32com.shell import shellcon

    python_exe = sys.executable

    if cmd_line is None:
        cmd_line = [python_exe] + sys.argv
    elif type(cmd_line) not in (types.TupleType,types.ListType):
        raise(ValueError, "cmdLine is not a sequence.")
    cmd = '"%s"' % (cmd_line[0],)
    # XXX TODO: isn't there a function or something we can call to massage command line params?
    params = " ".join(['"%s"' % (x,) for x in cmd_line[1:]])
    cmdDir = ''
    showCmd = win32con.SW_SHOWNORMAL
    #showCmd = win32con.SW_HIDE
    lpVerb = 'runas'  # causes UAC elevation prompt.

    # print "Running", cmd, params

    # ShellExecute() doesn't seem to allow us to fetch the PID or handle
    # of the process, so we can't get anything useful from it. Therefore
    # the more complex ShellExecuteEx() must be used.

    # procHandle = win32api.ShellExecute(0, lpVerb, cmd, params, cmdDir, showCmd)

    procInfo = ShellExecuteEx(nShow=showCmd,
                              fMask=shellcon.SEE_MASK_NOCLOSEPROCESS,
                              lpVerb=lpVerb,
                              lpFile=cmd,
                              lpParameters=params)

    if wait:
        procHandle = procInfo['hProcess']
        obj = win32event.WaitForSingleObject(procHandle, win32event.INFINITE)
        rc = win32process.GetExitCodeProcess(procHandle)
        #print "Process handle %s returned code %s" % (procHandle, rc)
    else:
        rc = None

    return rc


if __name__ == '__main__':
    get_drive_list()

    is_admin = is_user_admin()
    if is_admin:
        print("ADMIN")
        # Read the data from the drive
        read_drive(r"\\.\H")
        # Pause to get the stats
        input("Press any button to close the application")
    else:
        print("Application must be run as ADMIN")
        # Restart the application as ADMIN
        run_as_admin()

