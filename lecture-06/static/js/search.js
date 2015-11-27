$(function() {
    var host = window.location.hostname,
        port = window.location.port;

    $('#search').keyup(function(e) {
        var $resultTable = $('#result'),
            $spinner = $('.spinner'),
            $noHits = $('.no-hits'),
            forbiddenKeyCodes = [16, 17, 18, 91, 13, 93, 37, 38, 39, 40];

        if (forbiddenKeyCodes.indexOf(e.keyCode) == -1) {
            var query = $(this).val(),
                url = 'http://' + host + ':' + port + '/?q=' + query;

            if (query != '') {
                $resultTable.find('tbody').html('');
                $resultTable.hide();
                $noHits.hide();
                $spinner.show();
                $.get(url, function (result) {
                    if (result != '[]') {
                        var movies = $.parseJSON(result), list = '';
                        $resultTable.show();
                        $(movies).each(function(idx, movie) {
                            $resultTable.find('tbody').append(
                                $('<tr>').append(
                                    '<td>' + (idx + 1) + '</td>' +
                                    '<td>' + movie.title + '</td>' +
                                    '<td>' + movie.year + '</td>'
                                )
                            );
                        });
                        $spinner.hide();
                        $noHits.hide();
                    } else {
                        $spinner.hide();
                        $resultTable.find('tbody').html('');
                        $resultTable.hide();
                        $noHits.show();
                    }
                });
            } else {
                $spinner.hide();
                $noHits.hide();
                $resultTable.find('tbody').html('');
                $resultTable.hide();
            }
        }
    });
});