
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


});

function serialConnect() {
    console.log("CONNECT SERIAL");

    // grab values
    comm_port = $('#comm_port').val();
    baud_rate = $("#baud_rate").val();
    console.log(comm_port, baud_rate)
}