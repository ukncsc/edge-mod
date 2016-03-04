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
        graphModel.runModel();
    }

    ko.bindingHandlers.forceGraph = {
        nodeClass: "ko-d3-graph-node",
        init: function (element, valueAccessor, allBindings, viewModel, bindingContext) {
            // This will be called when the binding is first applied to an element
            // Set up any initial state, event handlers, etc. here
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
            // This will be called once when the binding is first applied to an element,
            // and again whenever any observables/computeds that are accessed change
            // Update the DOM element based on the supplied values here.
            var graphModel = valueAccessor()();
            var nodeContext = bindingContext.createChildContext(graphModel.nodes);
            ko.bindingHandlers.foreach.update(element, graphModel.nodes, allBindings, viewModel, nodeContext);

            var container = d3.select(element);
            var nodeSelector = container
                .selectAll("g." + ko.bindingHandlers.forceGraph.nodeClass)
                .data(graphModel.nodes());

            graphModel.d3Layout().on("tick", function () {
                nodeSelector.attr("transform", function (d) {
                    return "translate(" + d.x + "," + d.y + ")";
                })
            });
        }
    };
});
