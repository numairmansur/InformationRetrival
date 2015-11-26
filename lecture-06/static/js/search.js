$(function() {
    var host = window.location.hostname,
        port = window.location.port;

    $('#search').keyup(function(e) {
        var $resultArea = $('#result'),
            $spinner = $('.spinner'),
            forbiddenKeyCodes = [16, 17, 18, 91, 13, 93, 37, 38, 39, 40];

        if (forbiddenKeyCodes.indexOf(e.keyCode) == -1) {
            var query = $(this).val(),
                url = 'http://' + host + ':' + port + '/?q=' + query;

            if (query != '') {
                $resultArea.html('');
                $spinner.show();
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
        }
    });
});