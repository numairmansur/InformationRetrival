$(function() {
    var host = window.location.hostname,
        port = window.location.port;

    $('#search').keyup(function() {
        var query = $(this).val(),
            url = 'http://' + host + ':' + port + '/?q=' + query;

        if (query != '') {
            $.get(url, function (result) {
                $('#result').html('Result: ' + result);
            });
        } else {
            $('#result').html('');
        }
    });
});