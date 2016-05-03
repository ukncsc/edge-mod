define([
    "knockout",
    "dcl/dcl",
    "d3",
    "timeline/d3-tooltip"
], function (ko, declare, d3) {


    return declare(null, {

        constructor: function (div, rootId) {
            // pass in id of div where the svg will live and name/url of json data
            width = d3.select("#" + div)[0][0].clientWidth
            height = d3.select("#" + div)[0][0].clientHeight

            var margin = {
                    top: height / 6,
                    right: width / 7,
                    bottom: height / 10,
                    left: width / 7
                },
                radius = 1;

            svg_height = height - margin.top - margin.bottom

            graph_url = "/adapter/certuk_mod/ajax/incident_timeline/";
            d3.json(graph_url + encodeURIComponent(rootId), function (error, graph) {
                var tip = d3.tip().attr('class', 'd3-tip').html(function (d) {
                    return d.name + "<br>" + moment(d.date).utc().format("DD-MM-YYYY HH:mm:ss");
                });

                var originalNodeCount = graph.nodes.length;
                new_nodes = []

                graph.nodes.sort(function (a, b) {
                    return (new Date(a.date)) - (new Date(b.date));
                });

                var earliest = new Date(graph.nodes[0].date);
                var latest = new Date(graph.nodes[graph.nodes.length - 1].date);

                graph.nodes.forEach(function (node, index) {
                    new_nodes.push({name: "", date: node.date, type: "fixed"});
                    graph.links.push({source: index + originalNodeCount, target: index, type: "answeredby"});
                });

                graph.nodes = graph.nodes.concat(new_nodes);


                var svg = d3.select("#" + div)
                    .append("svg")
                    .attr("width", width)
                    .attr("height", svg_height)
                    .attr('transform', 'translate(' + margin.left + ',0)')
                    .attr('preserveAspectRatio', 'xMinYMin slice')
                    .append('g')
                    .attr('transform', 'translate(' + margin.left + ',0)')
                    .call(tip);

                var title = d3.select("#" + div + "_title");
                if (title) {
                    title.html("Timeline for " + graph.title);
                }

                /************************
                 Scales and Axes
                 *************************/

                //Used this custom format mainly to twiddle default us style %b %d to %d %b
                var customTimeFormat = d3.time.format.utc.multi([
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
                        return d.getDay() && d.getDate() != 1;
                    }],
                    ["%d %b", function (d) {
                        return d.getDate() != 1;
                    }],
                    ["%B", function (d) {
                        return d.getMonth();
                    }],
                    ["%Y", function () {
                        return true;
                    }]
                ]);

                var x = d3.time.scale()
                    .domain([earliest, latest])
                    .rangeRound([0, width - margin.left - margin.right])
                    .nice(5);

                var xAxis = d3.svg.axis()
                    .scale(x)
                    .orient('bottom')
                    .tickSize(2)
                    .ticks(10, 1)
                    .outerTickSize(5)
                    .tickFormat(customTimeFormat);

                var x2 = d3.time.scale()
                    .domain([earliest, latest])
                    .rangeRound([0, width - margin.left - margin.right]);


                svg.append('g')
                    .attr('class', 'x axis dayaxis')
                    .attr('transform', 'translate(0, ' + (svg_height - margin.top - margin.bottom) + ')')
                    .call(xAxis).selectAll("text")
                    .style("text-anchor", "end")
                    .attr("dx", "-.8em")
                    .attr("dy", ".15em")
                    .attr("transform", "rotate(-45)");

                svg.append('text')
                    .attr('transform', 'translate(0,'  + (svg_height - 15) + ')')
                    .style("text-anchor", "start")
                    .text("Times show are in the " + graph.tzname + " timezone")
                    .attr("dy", ".15em");

                /************************
                 Links
                 *************************/

                function linkArc(d) {

                    var dx = d.target.x - d.source.x,
                        dy = d.target.y - d.source.y,
                        dr = (d.straight == 0) ? Math.sqrt(dx * dx + dy * dy) : 0;
                    if (isNaN(dx) || isNaN(dy) || isNaN(dr)) {
                        return null;
                    }
                    return "M" + d.source.x + "," + d.source.y +
                        "A" + dr + "," + dr + " 0 0,1 " + d.target.x + "," + d.target.y;
                }

                var link = svg.selectAll(".link")
                    .data(graph.links)
                    .enter().append("svg:path", 'g')
                    .attr("d", function (d) {
                        return linkArc(d);
                    })
                    .attr("class", "link");

                /************************
                 Nodes
                 *************************/


                graph.nodes.forEach(function (node, index) {
                    // x is always over the sortdate
                    // y is stacked on any letters already on that date if the date is precise,
                    //   otherwise at top of graph to allow it to be pulled into position
                    node.x = x(new Date(node.date)) + (2 * radius);
                    if (node.type == "fixed") {
                        node.y = svg_height - margin.bottom - margin.top - radius - 1;
                        node.fixed = true;
                    } else {
                        half_height = svg_height / 2;
                        step = 1.2 * (half_height / (originalNodeCount + 3));
                        node.y = step * (index + 1) + margin.bottom;
                        node.fixed = true;
                    }
                });

                var node = svg.selectAll(".node")
                    .data(graph.nodes)
                    .enter().append("g")
                    .attr("class", "node")
                    .on('mouseover', tip.show)
                    .on('mouseout', tip.hide);


                // text, centered in node, with white shadow for legibility
                node.append("text")
                    .attr("text-anchor", "left")
                    .attr("dy", radius)
                    .attr("class", "shadow")
                    .text(function (d) {
                        return d.name
                    });
                node.append("text")
                    .attr("text-anchor", "left")
                    .attr("dy", radius)

                    .text(function (d) {
                        return d.name
                    });

                // on click, do something with id
                // implement this in a function outside this block


                /************************
                 Force and Tick
                 *************************/

                var force = self.force = d3.layout.force()
                    .nodes(graph.nodes)
                    .links(graph.links)
                    .charge(0)
                    .chargeDistance(0)
                    .gravity(0)
                    .linkStrength(1)
                    .size([width, svg_height])
                    .start()
                    .on("tick", tick);


                function tick(e) {

                    node.attr("transform", function (d) {
                        return "translate(" + d.x + "," + d.y + ")";
                    });

                    link.attr("d", function (d) {
                        return linkArc(d);
                    });

                    var ticks = svg.selectAll(".tick");
                    ticks[0][0].lastElementChild.innerHTML= moment(xAxis.scale().ticks()[0]).utc().format("DD-MM-YYYY hh:mm")
                }
            });
        }
    });
});
