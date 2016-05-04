define([
    "knockout",
    "d3",
    "jquery",
    "common/topic",
    "./topics",
    "./Graph"
], function (ko, d3, $, topic, topics) {
    "use strict";

    function needsResize(newWidth, newHeight, currentWidth, currentHeight) {
        return newWidth > 0
            && newHeight > 0
            && newWidth !== currentWidth
            && newHeight !== currentHeight;
    }

    function sizeToParent(element, graphModel) {
        var parent = $(element.parentNode);
        var height = parent.height();
        var width = parent.width();
        var currentSize = graphModel.size();
        if (needsResize(width, height, currentSize[0], currentSize[1])) {
            d3.select(element).attr("viewBox", "0 0 " + width + " " + height)
            graphModel.size([width, height]);
        }
    }

    ko.bindingHandlers.forceGraph = {
        nodeClass: "ko-d3-graph-node",
        linkClass: "ko-d3-graph-link",
        init: function (element, valueAccessor, allBindings, viewModel, bindingContext) {
            if (!(element.tagName === "svg")) {
                throw new Error("The 'forceGraph' binding can only be applied to 'svg' elements.");
            }

            var graphModel = valueAccessor()();
            var rootId = graphModel.findRootNode().id();
            ko.bindingHandlers["with"].init(element, valueAccessor, allBindings, viewModel, bindingContext)
            graphModel.applyBindingValues(allBindings());

            d3.select(window).on("resize", function () {
                sizeToParent(element, graphModel);
            });
            var handle = topic.subscribe(topics.RESIZE, function (id) {
                if (id === rootId) {
                    sizeToParent(element, graphModel);
                }
            });
            sizeToParent(element, graphModel);

            ko.utils.domNodeDisposal.addDisposeCallback(element, function () {
                handle.remove();
            });
            // Tell Knockout that we've already dealt with child bindings
            return {
                controlsDescendantBindings: true
            }
        },
        update: function (element, valueAccessor, allBindings, viewModel, bindingContext) {
            var graphModel = valueAccessor()();

            var container = d3.select(element);
            var nodeSelector = container
                .selectAll("." + ko.bindingHandlers.forceGraph.nodeClass)
                .data(graphModel.nodes())
                .call(graphModel.d3Layout().drag);

            var linkSelector = container
                .selectAll("." + ko.bindingHandlers.forceGraph.linkClass)
                .data(graphModel.links());

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
                    });
                });
        }
    };
});
