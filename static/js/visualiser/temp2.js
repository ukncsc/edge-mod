"use strict";

var width = 800;
var height = 600;

var container = d3.select("#tree-container").append("svg")
    .attr("width", width)
    .attr("height", height);

var graph = d3.layout.force()
    .size([width, height])
    .on("tick", onTick);

var linkSelector = container.selectAll(".link");
var nodeSelector = container.selectAll(".node");

d3.json("/adapter/visual_builder/view/fireeye:indicator-f7663237-55da-4d1c-aa52-6b24d39c47f7", function (error, response) {
    if (error) throw error;
    var graphData = response['graph'];
    var rootNode = graphData['nodes'][0];
    rootNode.x = 50;
    rootNode.y = height / 2;
    rootNode.fixed = true;
    updateGraph(graphData['nodes'], graphData['links']);
});

function updateGraph(nodeData, linkData) {



    linkSelector = linkSelector.data(linkData);
    linkSelector.exit().remove();
    var newLinkSelector = linkSelector.enter()
        .insert("line", ".node")
        .attr("class", "link");
    setLinkPositions(newLinkSelector);

    nodeSelector = nodeSelector.data(nodeData, function(n) { return n.id; });
    nodeSelector.exit().remove();
    var newNodeSelector = nodeSelector.enter()
        .append("circle")
        .attr("class", "node")
        .attr("r", 4.5)
        .append("text")
        .attr("x", 10)
        .attr("text-anchor", "end")
        .text(function (n) { return n.name; })
        .call(graph.drag);
    setNodePositions(newNodeSelector);

    graph.linkDistance(100)
        .charge(-500)
        .nodes(nodeData)
        .links(linkData)
        .start();
}

function onTick() {
    setLinkPositions(linkSelector);
    setNodePositions(nodeSelector);
}

function setLinkPositions(linkSelector) {
    linkSelector.attr("x1", function(d) { return d.source.x; })
      .attr("y1", function(d) { return d.source.y; })
      .attr("x2", function(d) { return d.target.x; })
      .attr("y2", function(d) { return d.target.y; });
}

function setNodePositions(nodeSelector) {
    nodeSelector.attr("cx", function(d) {
        return d.x;
    }).attr("cy", function(d) {
        return d.y;
    });
}
