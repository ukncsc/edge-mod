define([
    "knockout",
    "d3",
    "jquery",
    "common/topic",
    "./topics",
    "./Graph",
    "./ToolTip"
], function (ko, d3, $, topic, topics, Graph, ToolTip) {
    "use strict";

    function noPlusButton(hasBacklinks, hasMatches, isBackLinkShown, isMatchesShown) {
        return ((!hasBacklinks) && (!hasMatches)
        || (isBackLinkShown && isMatchesShown)
        || (hasMatches && isMatchesShown && !(hasBacklinks))
        || (hasBacklinks && isBackLinkShown && (!hasMatches)))
    }

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
            ko.bindingHandlers["with"].init(element, valueAccessor, allBindings, viewModel, bindingContext);
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

            viewModel.currentScale = 1;
            viewModel.currentXOffset = 0;
            viewModel.currentYOffset = 0;

            // Tell Knockout that we've already dealt with child bindings
            return {
                controlsDescendantBindings: true
            }
        },
        update: function (element, valueAccessor, allBindings, viewModel, bindingContext) {
            var graphModel = valueAccessor()();
            var container = d3.select(element);

            var nodeSelected = null;
            var nodeSelectedX = null;
            var nodeSelectedY = null;

            var minZoom = 0.3;
            var maxZoom = 5;

            var parent = d3.select(element.parentElement);

            var tooltip = new ToolTip(parent.select('#graph-node-tooltip'), container, viewModel);

            var zoom = d3.behavior.zoom()
                .scaleExtent([minZoom, maxZoom])
                .on("zoom", function (d, i) {
                    //Filter all but left mouse button
                    if (d3.event.sourceEvent === null || d3.event.sourceEvent.type !== 'wheel'
                        || d3.event.scale == viewModel.currentScale) {
                        return;
                    }

                    viewModel.currentScale = d3.event.scale;
                    graphModel.d3Layout().resume();
                });

            d3.behavior.zoom()
                .scale(viewModel.currentScale);

            /*The code below is ugly but is needed because d3 won't handle both .call(zoom) and .call(drag) on the container
             It's dragSuppress functionality is called twice and the unSuppress state reset gets confused. Only seems to be a problem
             for Firefox
             */

            function resetStyle() {
                var style = d3_documentElement(container[0][0]).style;
                style[d3_vendorSymbol(style, "userSelect")] = "";
            }

            /*copied from d3*/
            function d3_vendorSymbol(object, name) {
                if (name in object) return name;
                name = name.charAt(0).toUpperCase() + name.slice(1);
                for (var i = 0, n = d3_vendorPrefixes.length; i < n; ++i) {
                    var prefixName = d3_vendorPrefixes[i] + name;
                    if (prefixName in object) return prefixName;
                }
            }
            /*copied from d3*/
            var d3_vendorPrefixes = ["webkit", "ms", "moz", "Moz", "o", "O"];

            /*copied from d3*/
            function d3_documentElement(node) {
                return node && (node.ownerDocument || node.document || node).documentElement;
            }

            /*end*/

            var drag = d3.behavior.drag()
                .on("drag", function (d) {
                    //Filter all but left mouse button
                    if (d3.event.sourceEvent === null || d3.event.sourceEvent.button !== 0) {
                        return;
                    }

                    d3.event.sourceEvent.preventDefault();

                    if (nodeSelected !== null) {
                        updateDraggedNode(nodeSelected);
                    }
                    else {
                        viewModel.currentXOffset = viewModel.currentXOffset + d3.event.dx;
                        viewModel.currentYOffset = viewModel.currentYOffset + d3.event.dy;
                    }
                    graphModel.d3Layout().resume();
                })
                .on("dragend", function (d) {
                    nodeSelected = null;
                    resetStyle();
                });


            function updateDraggedNode(d) {
                nodeSelectedX = d.x = d.x + d3.event.dx / viewModel.currentScale;
                nodeSelectedY = d.y = d.y + d3.event.dy / viewModel.currentScale;
            }

            var nodeSelector = container
                .selectAll("." + ko.bindingHandlers.forceGraph.nodeClass)
                .data(graphModel.nodes())
                .on("mousedown", function (d) {
                    graphModel.d3Layout().stop();
                    nodeSelected = d;})
                .on("click", function (d) {
                    if (!nodeSelected) {
                        viewModel.onNodeClicked(d);
                    }
                });

            var matchingAndBacklinks = container
                .selectAll("." + ko.bindingHandlers.forceGraph.nodeClass)
                .data(graphModel.nodes()).on("mousemove", function (d) {
                    tooltip.setNodeTooltip(d, viewModel.currentScale, viewModel.currentXOffset, viewModel.currentYOffset);
                });

            container.on("mouseover", function (d) {
                tooltip.hide();
            });


            var showMatchingAndBacklinks = container
                .selectAll("." + ko.bindingHandlers.forceGraph.nodeClass);

            var linkSelector = container
                .selectAll("." + ko.bindingHandlers.forceGraph.linkClass)
                .data(graphModel.links());

            container.call(zoom).call(drag);
            graphModel
                .d3Layout()
                .on("tick", function () {
                    var viewBox = container.node().viewBox;
                    var x_middle = viewBox.animVal != null ? viewBox.animVal.width / 2 : 0;
                    var y_middle = viewBox.animVal != null ? viewBox.animVal.height / 2 : 0;

                    nodeSelector.attr("transform", function (d) {
                        if (d === nodeSelected) { //Without this, the dragged node jumps out double its dragged distance
                            d.x = nodeSelectedX;
                            d.y = nodeSelectedY;
                        }

                        return "translate(" + ((x_middle + (d.x - x_middle) * viewModel.currentScale) + viewModel.currentXOffset)
                            + "," + ((y_middle + (d.y - y_middle) * viewModel.currentScale) + viewModel.currentYOffset)
                            + ")scale(" + viewModel.currentScale + ")";
                    });

                    linkSelector.attr("x1", function (d) {
                            return (x_middle + (d.source.x - x_middle) * viewModel.currentScale) + viewModel.currentXOffset;
                        })
                        .attr("y1", function (d) {
                            return (y_middle + (d.source.y - y_middle) * viewModel.currentScale) + viewModel.currentYOffset;
                        })
                        .attr("x2", function (d) {
                            return (x_middle + (d.target.x - x_middle) * viewModel.currentScale) + viewModel.currentXOffset;
                        })
                        .attr("y2", function (d) {
                            return (y_middle + (d.target.y - y_middle) * viewModel.currentScale) + viewModel.currentYOffset;
                        });
                })
        }
    };
});
