define([
    "knockout",
    "d3",
    "jquery",
    "./Graph"
], function (ko, d3, $) {
    "use strict";

    function sizeToParent(element, graphModel) {
        var parent = $(element.parentNode);
        var height = parent.height();
        var width = parent.width();
        d3.select(element)
            .attr("viewBox", "0 0 " + width + " " + height)
            .attr("height", height)
            .attr("width", width);
        graphModel.size([width, height]);
    }

    ko.bindingHandlers.forceGraph = {
        nodeClass: "ko-d3-graph-node",
        linkClass: "ko-d3-graph-link",
        init: function (element, valueAccessor, allBindings, viewModel, bindingContext) {
            if (!(element.tagName === "svg")) {
                throw new Error("The 'forceGraph' binding can only be applied to 'svg' elements.");
            }
            if (!(element.firstElementChild && element.firstElementChild.tagName === "g")) {
                throw new Error("The node template must be a 'g' element.");
            }
            element.firstElementChild.setAttribute("class", ko.bindingHandlers.forceGraph.nodeClass);

            var graphModel = valueAccessor()();
            var nodeContext = bindingContext.createChildContext(graphModel.nodes);
            ko.bindingHandlers.foreach.init(element, graphModel.nodes, allBindings, viewModel, nodeContext);
            graphModel.applyBindingValues(allBindings());

            d3.select(window).on("resize", function () {
                sizeToParent(element, graphModel);
            });
            sizeToParent(element, graphModel);

            // Tell Knockout that we've already dealt with child bindings
            return {
                controlsDescendantBindings: true
            }
        },
        update: function (element, valueAccessor, allBindings, viewModel, bindingContext) {
            var graphModel = valueAccessor()();
            var nodeContext = bindingContext.createChildContext(graphModel.nodes);
            ko.bindingHandlers.foreach.update(element, graphModel.nodes, allBindings, viewModel, nodeContext);

            var container = d3.select(element);
            var nodeSelector = container
                .selectAll("g." + ko.bindingHandlers.forceGraph.nodeClass)
                .data(graphModel.nodes())
                .call(graphModel.d3Layout().drag);

            var linkSelector = container
                .selectAll("g." + ko.bindingHandlers.forceGraph.linkClass)
                .data(graphModel.links());

            linkSelector.exit().remove();
            linkSelector.enter()
                .append("line")
                .attr("class", ko.bindingHandlers.forceGraph.linkClass);

            // We need to reorder the nodes so they appear on top of the links
            // Swapping the order of node/link creation has no effect...
            container
                .selectAll("g." + ko.bindingHandlers.forceGraph.nodeClass)[0]
                .forEach(function (n) {
                    n.parentNode.appendChild(n);
                });

            graphModel
                .d3Layout()
                .on("tick", function () {
                    linkSelector.attr("x1", function (d) {
                            return d.source.x;
                        })
                        .attr("y1", function (d) {
                            return d.source.y;
                        })
                        .attr("x2", function (d) {
                            return d.target.x;
                        })
                        .attr("y2", function (d) {
                            return d.target.y;
                        });
                    nodeSelector.attr("transform", function (d) {
                        return "translate(" + d.x + "," + d.y + ")";
                    })
                });
        }
    };
});
