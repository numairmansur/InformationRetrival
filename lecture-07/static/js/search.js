$(function() {
    var host = window.location.hostname,
        port = window.location.port,
        requestPool = [];

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

                // Abort any other requests
                $(requestPool).each(function(idx, request) {
                    request.abort();
                });
                requestPool = [];

                requestPool.push($.get(url, function(result) {
                    if (result != '[]') {
                        var cities = $.parseJSON(result);
                        $resultTable.show();
                        $(cities).each(function(idx, city) {
                            $resultTable.find('tbody').append(
                                $('<tr>').append(
                                    '<td>' + (idx + 1) + '</td>' +
                                    '<td>' + city.city + '</td>' +
                                    '<td>' + city.country_code + '</td>' +
                                    '<td>' + city.population + '</td>'
                                )
                            );
                        });
                        $noHits.hide();
                    } else {
                        $resultTable.find('tbody').html('');
                        $resultTable.hide();
                        $noHits.show();
                    }
                    $spinner.hide();
                }));
            } else {
                $spinner.hide();
                $noHits.hide();
                $resultTable.find('tbody').html('');
                $resultTable.hide();
            }
        }
    });
});