plot = function(json) {
    $('#text').val(json);
    var elementsData = eval('('+json+')');
    console.log("Data loaded", elementsData);

    $('#cy').cytoscape({
        layout: {
            name: 'cose',
            padding: 10,
            randomize: true
        },

        style: cytoscape.stylesheet()
            .selector('node')
                .css({
                    'shape': 'data(faveShape)',
                    'width': 'mapData(weight, 40, 80, 20, 60)',
                    'content': 'data(name)',
                    'text-valign': 'center',
                    'text-outline-width': 2,
                    'text-outline-color': 'data(faveColor)',
                    'background-color': 'data(faveColor)',
                    'color': '#fff'
                })
            .selector(':selected')
                .css({
                    'border-width': 3,
                    'border-color': '#333'
                })
            .selector('edge')
                .css({
                    'curve-style': 'bezier',
                    'opacity': 0.666,
                    'width': 'mapData(strength, 70, 100, 2, 6)',
                    'target-arrow-shape': 'triangle',
                    'source-arrow-shape': 'circle',
                    'line-color': 'data(faveColor)',
                    'source-arrow-color': 'data(faveColor)',
                    'target-arrow-color': 'data(faveColor)',
                    'label': 'data(label)'
                })
            .selector('edge.questionable')
                .css({
                    'line-style': 'dotted',
                    'target-arrow-shape': 'diamond'
                })
            .selector('.faded')
                .css({
                    'opacity': 0.25,
                    'text-opacity': 0
                }),

        elements: elementsData,

        ready: function() {
            window.cy = this
        }
    });
};

$(function(){
    $("#submit").click(function() {
        plot($("#text").val())
    });

    var source = window.location.href;
    var ix = source.indexOf('?');
    if (ix >= 0) {
        source = source.substring(ix+1);
        console.log('Using source', source)
        $.get(source+".json")
            .fail(function(jqxhr, textStatus, error) {
                var err = textStatus + ", " + error;
                console.log("Request failed", err);
            })
            .done(function(jsonString) {
                plot(jsonString);
            })

    }
});

