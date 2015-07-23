var _ = require('lodash'),
    d3 = require('d3'),
    moment = require('moment'),
    data = {},
    _max = 0;

d3.selectAll('.chart')[0].forEach(function(container) {
    var day = d3.select(container).attr('data-day'),
    _y = 0;

    data[day] = [];
    _.forEach(CONFIG.bins[day], function(vals, time) {
        var ts = moment(day + 'T' + time)._d;
        _y += (vals.check_in || 0) - (vals.check_out || 0);
        _max = Math.max(_max, _y);
        data[day].push({
            x: ts,
            y: _y
        });
    });
});



function chart(container) {
    var day = container.attr('data-day');
    var margin = {top: 20, right: 20, bottom: 30, left: 50},
        width = 960 - margin.left - margin.right,
        height = 500 - margin.top - margin.bottom;

    var x = d3.time.scale()
        .domain([
            moment(day + 'T' + CONFIG.start_time),
            moment(day + 'T' + CONFIG.end_time),
        ])
        .range([0, width]);

    var y = d3.scale.linear()
        .domain([0, _max])
        .range([height, 0]);

    var xAxis = d3.svg.axis()
        .scale(x)
        .orient("bottom");

    var yAxis = d3.svg.axis()
        .scale(y)
        .orient("left");

    var line = d3.svg.line()
        .x(function(d) { return x(d.x); })
        .y(function(d) { return y(d.y); });

    var svg = container.append("svg")
        .attr("width", width + margin.left + margin.right)
        .attr("height", height + margin.top + margin.bottom)
      .append("g")
        .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

    svg.append("g")
        .attr("class", "x axis")
        .attr("transform", "translate(0," + height + ")")
        .call(xAxis);

    svg.append("g")
        .attr("class", "y axis")
        .call(yAxis)
        .append("text")
        .attr("transform", "rotate(-90)")
        .attr("y", 6)
        .attr("dy", ".71em")
        .style("text-anchor", "end")
        .text("Kinder");

    svg.append("path")
        .datum(data[day])
        .attr("class", "line")
        .attr("d", line);

    svg.append("rect")
        .attr("class", "overlay")
        .attr("width", width)
        .attr("height", height)
        .on("mouseover", function() { focus.style("display", null); })
        .on("mouseout", function() { focus.style("display", "none"); })
        .on("mousemove", mousemove);

    var bisectDate = d3.bisector(function(d) { return d.x; }).left;
    var focus = svg.append("g")
        .attr("class", "focus")
        .style("display", "none");

    focus.append("circle")
        .attr("r", 6.5);

    focus.append("text")
        .attr("x", 9)
        .attr("dy", "0.5em");

    function mousemove() {
        var x0 = x.invert(d3.mouse(this)[0]),
            i = bisectDate(data[day], x0, 1),
            d0 = data[day][i - 1],
            d1 = data[day][i],
            d = x0 - d0.x > d1.x - x0 ? d1 : d0;
        focus.attr("transform", "translate(" + x(d.x) + "," + y(d.y) + ")");
        var text = moment(d.x).format('HH:mm') + ': ' + d.y;
        focus.select("text").text(text);
    }
}


d3.selectAll('.chart')[0].forEach(function(container) {
    chart(d3.select(container));
});
