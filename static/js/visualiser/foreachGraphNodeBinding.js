"use strict";

ko.bindingHandlers.foreachGraphNode = {
    nodeClass: "ko-d3-graph-node",
    getWrappedNodeArray: function (valueAccessor) {
        return function () {
            return ko.unwrap(valueAccessor()).nodes;
        }
    },
    init: function (element, valueAccessor, allBindings, viewModel, bindingContext) {
        if (element.tagName !== "svg") {
            throw new Error("The 'foreachGraphNode' binding can only be applied to svg elements.");
        }

        if (element.children.length !== 0 && element.children[0].tagName !== "g") {
            // Would like to be able to wrap the template in a <g> here, rather than enforce it.
            // But if we do, it doesn't render.
            throw new Error("The node template must be a group element.");
        }

        var svg = d3.select(element).call(d3.behavior.zoom().on("zoom", function () {
            svg.attr("transform", "translate(" + d3.event.translate + ")" + " scale(" + d3.event.scale + ")")
        }));
        element.children[0].setAttribute("class", ko.bindingHandlers.foreachGraphNode.nodeClass);

        var nodeArray = ko.bindingHandlers.foreachGraphNode.getWrappedNodeArray(valueAccessor);

        var nodeContext = bindingContext.createChildContext(nodeArray);
        ko.bindingHandlers.foreach.init(element, nodeArray, allBindings, viewModel, nodeContext);

        // Setup/store the force directed layout
        // Need to apply default width/height if none supplied
        // Even better, make this resize... (although D3 needs to know width/height beforehand)
        valueAccessor.graph = d3.layout.force()
            .linkDistance(200)
            .gravity(0.025)
            .friction(0.85)
            .charge(-500); // Make these available in the binding

        function applySizeToGraph() {
            var ele = $(element);
            var width = ele.width();
            var height = ele.height();
            d3.select(element).attr("viewBox", "0 0 " + width + " " + height);
            valueAccessor.graph
                .size([width, height])
                .start();
        }

        d3.select(window).on("resize", applySizeToGraph);
        applySizeToGraph();

        // Tell Knockout that we've already dealt with child bindings
        return {controlsDescendantBindings: true}
    },
    update: function (element, valueAccessor, allBindings, viewModel, bindingContext) {
        var nodeArray = ko.bindingHandlers.foreachGraphNode.getWrappedNodeArray(valueAccessor);
        var linkData = ko.unwrap(valueAccessor()).links;

        var nodeContext = bindingContext.createChildContext(nodeArray);
        // This will render the array of nodes...
        ko.bindingHandlers.foreach.update(element, nodeArray, allBindings, viewModel, nodeContext);

        var container = d3.select(element);
        var unwrappedNodeArray = nodeArray();
        // D3 does its own data binding to elements
        // All elements should exist at this point, so we only need to do this so D3 knows where the
        // node position data lives.
        var nodeSelector = container.selectAll("g." + ko.bindingHandlers.foreachGraphNode.nodeClass)
            .data(unwrappedNodeArray);

        // Let D3 add/remove/bind links
        var linkSelector = container.selectAll("line.ko-d3-graph-link");
        linkSelector = linkSelector.data(linkData);
        linkSelector.exit().remove();
        linkSelector.enter()
            .append("line")
            .attr("class", "ko-d3-graph-link")
            .style("stroke", "#333")
            .style("stroke-width", "0.5"); // Grab line styling from another binding...

        // We need to reorder the nodes so they appear on top of the links
        // Swapping the order of node/link creation has no effect...
        container.selectAll("g." + ko.bindingHandlers.foreachGraphNode.nodeClass)[0]
            .forEach(function (n) {
                n.parentNode.appendChild(n);
            });

        valueAccessor.graph
            .nodes(unwrappedNodeArray)
            .links(linkData)
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
            })
            .start(); // Start the simulation, and call the "tick" handler for each advance of the animation
    }
};

