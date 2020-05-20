
$(document).ready(function() {
    /** 
    $('form').submit(function (e) {
        console.log("CONNECT to Serial Port")

        // grab values
        comm_port = $('input[name="comm_port"]').val();
        baud_rate = $('input[name="baud_rate"]').val();
        console.log(comm_port, baud_rate)

        scan = $('#btnScan').val();
        connect = $('input[name="btnConnect"]').val();
        disconnect = $('input[name="btnDisconnect"]').val();
        console.log(scan)
        console.log(connect)
        console.log(disconnect)

        //var url = "{{ url_for('/serial_connect') }}"; // send the form data here.
        $.ajax({
            type: "POST",
            url: "/serial_connect",
            data: $('form').serialize(), // serializes the form's elements.
            success: function (data) {
                console.log(data)  // display the returned data in the console.
            }
        });
        e.preventDefault(); // block the traditional submission of the form.
    });
    */

    /**
     * Handle the Serial port SCAN button.
     * This will reset the serial port list
     * then set the previously selected COMM port.
     */
    $('#btnScan').click(function() {
        console.log("SCAN BUTTON CLICKED")

        // grab values
        comm_port = $('#comm_port').val();
        baud_rate = $("#baud_rate").val();
        console.log(comm_port, baud_rate)

        $.ajax({
            type: "POST",
            url: "/serial_scan",
            data: $('form').serialize(), // serializes the form's elements.
            success: function (response) {
                console.log(response)  // display the returned data in the console.
                // Clear the list then Update the list of comm ports
                $("#comm_port").empty();
                response.data.port_list.forEach(function(item) {
                    //console.log(response.data.port_list[i]);
                    $("#comm_port").append(new Option(item, item));
                });

                // Reselect the original selections
                $('#comm_port').val(comm_port);
            }
        });
    });


    /**
     * Handle the Serial port SCAN button.
     * This will reset the serial port list
     * then set the previously selected COMM port.
     */
    $('#btnConnect').click(function() {
        console.log("CONNECT BUTTON CLICKED")

        // grab values
        comm_port = $('#comm_port').val();
        baud_rate = $("#baud_rate").val();
        console.log(comm_port, baud_rate)

        $.ajax({
            type: "POST",
            url: "/serial_connect",
            data: $('form').serialize(), // serializes the form's elements.
            success: function (response) {
                console.log(response)  // display the returned data in the console.

            }
        });

        // Inject our CSRF token into our AJAX request.
        // REALLY JUST REQUIRED FOR WEB USE
        $.ajaxSetup({
            beforeSend: function(xhr, settings) {
                if (!/^(GET|HEAD|OPTIONS|TRACE)$/i.test(settings.type) && !this.crossDomain) {
                    xhr.setRequestHeader("X-CSRFToken", "{{ form.csrf_token._value() }}")
                }
            }
        })
    });

    /**
     * Handle the Serial port SCAN button.
     * This will reset the serial port list
     * then set the previously selected COMM port.
     */
    $('#btnDisconnect').click(function() {
        console.log("DISCONNECT BUTTON CLICKED")

        // grab values
        comm_port = $('#comm_port').val();
        baud_rate = $("#baud_rate").val();
        console.log(comm_port, baud_rate)

        $.ajax({
            type: "POST",
            url: "/serial_disconnect",
            data: $('form').serialize(), // serializes the form's elements.
            success: function (response) {
                console.log(response)  // display the returned data in the console.
            }
        });

        // Inject our CSRF token into our AJAX request.
        // REALLY JUST REQUIRED FOR WEB USE
        $.ajaxSetup({
            beforeSend: function(xhr, settings) {
                if (!/^(GET|HEAD|OPTIONS|TRACE)$/i.test(settings.type) && !this.crossDomain) {
                    xhr.setRequestHeader("X-CSRFToken", "{{ form.csrf_token._value() }}")
                }
            }
        })
    });


    /**
     * Handle the Serial port SCAN button.
     * This will reset the serial port list
     * then set the previously selected COMM port.
     */
    $('#btnBrowseFolder').click(function() {
        console.log("Browse Folder")

        // grab values
        comm_port = $('#comm_port').val();
        baud_rate = $("#baud_rate").val();
        console.log(comm_port, baud_rate)

        $.ajax({
            type: "POST",
            url: "/browse_folder",
            data: $('form').serialize(), // serializes the form's elements.
            success: function (response) {
                console.log(response)  // display the returned data in the console.

            }
        });

        // Inject our CSRF token into our AJAX request.
        // REALLY JUST REQUIRED FOR WEB USE
        $.ajaxSetup({
            beforeSend: function(xhr, settings) {
                if (!/^(GET|HEAD|OPTIONS|TRACE)$/i.test(settings.type) && !this.crossDomain) {
                    xhr.setRequestHeader("X-CSRFToken", "{{ form.csrf_token._value() }}")
                }
            }
        })
    });

    /**
     * Handle downloading.
     */
    $('#btnDownload').click(function() {
        console.log("Download")

        // grab values
        comm_port = $('#comm_port').val();
        baud_rate = $("#baud_rate").val();
        console.log(comm_port, baud_rate)

        $.ajax({
            type: "POST",
            url: "/download",
            data: $('form').serialize(), // serializes the form's elements.
            success: function (response) {
                console.log(response)  // display the returned data in the console.

            }
        });

        // Inject our CSRF token into our AJAX request.
        // REALLY JUST REQUIRED FOR WEB USE
        $.ajaxSetup({
            beforeSend: function(xhr, settings) {
                if (!/^(GET|HEAD|OPTIONS|TRACE)$/i.test(settings.type) && !this.crossDomain) {
                    xhr.setRequestHeader("X-CSRFToken", "{{ form.csrf_token._value() }}")
                }
            }
        })
    });

    // Use a "/test" namespace.
    // An application can open a connection on multiple namespaces, and
    // Socket.IO will multiplex all those connections on a single
    // physical channel. If you don't care about multiple channels, you
    // can set the namespace to an empty string.
    namespace = '/test';

    // Connect to the Socket.IO server.
    // The connection URL has the following format, relative to the current page:
    //     http[s]://<domain>:<port>[/<namespace>]
    var socket = io(namespace);

    // Event handler for new connections.
    // The callback function is invoked when a connection with the
    // server is established.
    socket.on('connect', function() {
        socket.emit('my_event', {data: 'I\'m connected!'});
    });

    // Event handler for server sent data.
    // The callback function is invoked whenever the server emits data
    // to the client. The data is then displayed in the "Received"
    // section of the page.
    socket.on('status_report', function(msg, cb) {
        //$('#log').append('<br>' + $('<div/>').text('Received #' + msg.count + ': ' + msg.data).html());
        //if (cb)
        //    cb();
    });

        // Event handler for server sent data.
    // The callback function is invoked whenever the server emits data
    // to the client. The data is then displayed in the "Received"
    // section of the page.
    socket.on('gui_status', function(msg, cb) {
        //$('#dl_status').append('<br>' + $('<div/>').text('Received #' + msg.count + ': ' + msg).html());
        json_msg = JSON.parse(msg)
        console.log(msg)
        console.log(json_msg.dl_status.TotalBlocks)
        console.log(json_msg.dl_status.FolderPath)
        //if (cb)
        //    cb();
        $("#totalBlocks").html(json_msg.dl_status.PrettyTotalBlocks.toString());
        $("#blocksRead").html(json_msg.dl_status.PrettyBlocksRead.toString());
        $("#blocksLeft").html(json_msg.dl_status.PrettyBlocksLeft.toString());
        $("#folderPath").html(json_msg.dl_status.FolderPath.toString());
        $("#downloadProgress").html(json_msg.dl_status.DownloadProgress.toString());
        $( "#progressbar" ).progressbar({ value: json_msg.dl_status.DownloadProgress });

        //$('#btnConnect').disabled = json_msg.btn_connect_enable;
        //$('#btnDisconnect').disabled = json_msg.btn_disconnect_enable;
        document.getElementById("btnConnect").disabled = json_msg.btn_connect_disabled
        document.getElementById("btnDisconnect").disabled = json_msg.btn_disconnect_disabled
        document.getElementById("btnScan").disabled = json_msg.btn_scan_disabled
        document.getElementById("btnDownload").disabled = json_msg.btn_download_disabled
    });

});
