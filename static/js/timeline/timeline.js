define([
    "dcl/dcl",
    "d3",
    "common/moment-shim",
    "common/modal/show-error-modal",
    "timeline/d3-tooltip"
], function (declare, d3, moment, showErrorModal, errorContentTemplate) {
    "use strict";
    return declare(null, {

        create_timeline: function (div, rootId, graph_url) {
            var elem = d3.select("#" + div)[0][0];
            if (elem ===  null) {
                return;
            }
            var width = elem.clientWidth,
                height = elem.clientHeight,
                margin = {
                    top: height / 6,
                    right: width / 7,
                    bottom: height / 10,
                    left: width / 7
                },

                radius = 1,
                svg_height = height - margin.top - margin.bottom,
                half_height = (svg_height / 2);

            d3.json(graph_url + encodeURIComponent(rootId), function (error, graph) {
                if (error !== null) {
                    showErrorModal(JSON.parse(error.response).message, false);
                    return;
                }

                graph.nodes.sort(function (a, b) {
                    return (new Date(a.date)) - (new Date(b.date));
                });


                var tip = d3.tip().attr('class', 'd3-tip').html(function (d) {
                        return d.name + "<br>" + moment(d.date).utc().format("DD-MM-YYYY HH:mm:ss");
                    }),
                    numberPointsCount = graph.nodes.length,
                    earliest = new Date(graph.nodes[0].date),
                    latest = new Date(graph.nodes[graph.nodes.length - 1].date),
                    step = 1.2 * (half_height / (numberPointsCount + 3)),
                    svg,
                    title,
                    customTimeFormat,
                    x,
                    xAxis,
                    link,
                    node,
                    force,
                    ticks;

                graph.nodes.forEach(function (node, index) {
                    graph.nodes.push({name: "", date: node.date, type: "onAxis"});
                    graph.links.push({source: index + numberPointsCount, target: index});
                });

                svg = d3.select("#" + div)
                    .append("svg")
                    .attr("width", width)
                    .attr("height", svg_height)
                    .attr('preserveAspectRatio', 'xMinYMin slice')
                    .append('g')
                    .attr('transform', 'translate(' + margin.left + ',0)')
                    .call(tip);

                title = d3.select("#" + div + "_title");
                if (title) {
                    title.html("Timeline for " + graph.title);
                }

                /************************
                 Scales and Axes
                 *************************/

                    //Used this custom format mainly to twiddle default us style %b %d to %d %b
                customTimeFormat = d3.time.format.utc.multi([
                    [".%L", function (d) {
                        return d.getMilliseconds();
                    }],
                    [":%S", function (d) {
                        return d.getSeconds();
                    }],
                    ["%I:%M", function (d) {
                        return d.getMinutes();
                    }],
                    ["%I %p", function (d) {
                        return d.getHours();
                    }],
                    ["%d %b", function (d) {
                        return d.getDay() && d.getDate() !== 1;
                    }],
                    ["%d %b", function (d) {
                        return d.getDate() !== 1;
                    }],
                    ["%B", function (d) {
                        return d.getMonth();
                    }],
                    ["%Y", function () {
                        return true;
                    }]
                ]);

                x = d3.time.scale()
                    .domain([earliest, latest])
                    .rangeRound([0, width - margin.left - margin.right])
                    .nice(5);

                xAxis = d3.svg.axis()
                    .scale(x)
                    .orient('bottom')
                    .tickSize(2)
                    .ticks(10, 1)
                    .outerTickSize(5)
                    .tickFormat(customTimeFormat);

                svg.append('g')
                    .attr('class', 'x axis dayaxis')
                    .attr('transform', 'translate(0, ' + (svg_height - margin.top - margin.bottom) + ')')
                    .call(xAxis).selectAll("text")
                    .style("text-anchor", "end")
                    .attr("dx", "-.8em")
                    .attr("dy", ".15em")
                    .attr("transform", "rotate(-45)");

                svg.append('text')
                    .attr('transform', 'translate(0,' + (svg_height - 15) + ')')
                    .style("text-anchor", "start")
                    .text("Times show are in the " + graph.tzname + " timezone")
                    .attr("dy", ".15em");


                /************************
                 Nodes
                 *************************/

                graph.nodes.forEach(function (node, index) {
                    node.x = x(new Date(node.date)) + (2 * radius);
                    if (node.type === "onAxis") {  //
                        node.y = svg_height - margin.bottom - margin.top - radius - 1;
                        node.fixed = true;
                    } else {
                        //Step labels down from near top to x-axis so as to avoid collisions
                        node.y = step * (index + 1) + margin.bottom;
                        node.fixed = true;
                    }
                });

                node = svg.selectAll(".node")
                    .data(graph.nodes)
                    .enter().append("g")
                    .attr("class", "node")
                    .attr('transform', function (d) {
                        return "translate(" + d.x + "," + d.y + ")";
                    })
                    .on('mouseover', tip.show)
                    .on('mouseout', tip.hide);

                node.append("text")
                    .attr("text-anchor", "left")
                    .attr("dy", radius)
                    .attr("class", "shadow")
                    .text(function (d) {
                        return d.name;
                    });

                node.append("text")
                    .attr("text-anchor", "left")
                    .attr("dy", radius)
                    .text(function (d) {
                        return d.name;
                    });

                /************************
                 Links
                 *************************/

                function linkArc(d) {
                    var dx = d.target.x - d.source.x,
                        dy = d.target.y - d.source.y,
                        dr = (d.straight === 0) ? Math.sqrt(dx * dx + dy * dy) : 0;
                    if (isNaN(dx) || isNaN(dy) || isNaN(dr)) {
                        return null;
                    }
                    return "M" + d.source.x + "," + d.source.y +
                        "A" + dr + "," + dr + " 0 0,1 " + d.target.x + "," + d.target.y;
                }

                link = svg.selectAll(".link")
                    .data(graph.links)
                    .enter().append("svg:path", 'g')
                    .attr("class", "link");

                /************************
                 Force and Tick
                 *************************/

                force = d3.layout.force()
                    .nodes(graph.nodes)
                    .links(graph.links)
                    .charge(0)
                    .chargeDistance(0)
                    .gravity(0)
                    .linkStrength(1)
                    .size([width, svg_height])
                    .start();

                force.stop();

                ticks = svg.selectAll(".tick");
                ticks[0][0].lastElementChild.innerHTML = moment(xAxis.scale().ticks()[0]).utc().format("DD-MM-YYYY hh:mm");

                link.attr("d", function (d) {
                    return linkArc(d);
                });

            });
        }
    });
});
