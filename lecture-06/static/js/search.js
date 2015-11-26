$(function() {
    var host = window.location.hostname,
        port = window.location.port;

    $('#search').keyup(function() {
        var $resultArea = $('#result'),
            $spinner = $('.spinner');

        $resultArea.html('');
        $spinner.show();

        // TODO: filter key presses, don't take Shift, Ctrl, Cmd, Alt into
        // account, otherwise, extra requests will be sent -> BAD performance

        var query = $(this).val(),
            url = 'http://' + host + ':' + port + '/?q=' + query;

        if (query != '') {
            $.get(url, function (result) {
                if (result != '[]') {
                    var movies = $.parseJSON(result), list = '';
                    $(movies).each(function(idx, movie) {
                        list += '<li>'+ movie.title + ' (' + movie.year + ')</li>';
                    });
                    $spinner.hide();
                    $resultArea.html('<ul>' + list + '</ul>');
                } else {
                    $spinner.hide();
                    $resultArea.html('No hits :(');
                }
            });
        } else {
            $spinner.hide();
            $resultArea.html('');
        }
    });
});