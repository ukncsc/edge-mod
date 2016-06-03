define([
    "knockout",
    "d3",
    "jquery",
    "common/topic",
    "./topics",
    "./Graph"
], function (ko, d3, $, topic, topics) {
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
            // Tell Knockout that we've already dealt with child bindings
            return {
                controlsDescendantBindings: true
            }
        },
        update: function (element, valueAccessor, allBindings, viewModel, bindingContext) {
            var graphModel = valueAccessor()();
            var container = d3.select(element);

            var currentScale = 1;
            var currentXOffset = 0;
            var currentYOffset = 0;

            var nodeSelected = null;
            var nodeSelectedX = null;
            var nodeSelectedY = null;

            var minZoom = 0.3;
            var maxZoom = 5;

            var tooltip = d3.select("#graph-node-tooltip");

            var zoom = d3.behavior.zoom()
                .scaleExtent([minZoom, maxZoom])
                .on("zoom", function (d, i) {
                    //Filter all but left mouse button
                    if (d3.event.sourceEvent === null || d3.event.sourceEvent.which !== 1
                        || d3.event.scale == currentScale) {
                        return;
                    }

                    currentScale = d3.event.scale;
                    graphModel.d3Layout().resume();
                });

            var drag = d3.behavior.drag()
                .on("drag", function (d) {
                    //Filter all but left mouse button
                    if (d3.event.sourceEvent === null || d3.event.sourceEvent.which !== 1) {
                        return;
                    }

                    if (nodeSelected !== null) {
                        updateDraggedNode(nodeSelected);
                    }
                    else {
                        currentXOffset = currentXOffset + d3.event.dx;
                        currentYOffset = currentYOffset + d3.event.dy;
                    }
                    graphModel.d3Layout().resume();
                })
                .on("dragend", function (d) {
                    nodeSelected = null;
                });

            var dragNode = d3.behavior.drag()
                .on("dragstart", function (d) {
                    graphModel.d3Layout().stop();
                    nodeSelected = d;
                });


            function updateDraggedNode(d) {
                nodeSelectedX = d.x = d.x + d3.event.dx / currentScale;
                nodeSelectedY = d.y = d.y + d3.event.dy / currentScale;
            }

            var nodeSelector = container
                .selectAll("." + ko.bindingHandlers.forceGraph.nodeClass)
                .data(graphModel.nodes()).call(dragNode);

            function getBacklinkAddButton(id, backlinksShown, hasBacklinks) {
                return ((!hasBacklinks) || (hasBacklinks && backlinksShown)) ? "" : "<button type=\"button\" class=\"btn btn-default clear_bg\" aria-label=\"Left Align\" data-bind=\"click:$data.onPlusBacklinkClicked.bind($data,'" + id + "')\"><span class='green glyphicon glyphicon-arrow-left clear_bg'/></button>";
            }

            function getBacklinkMinusButton(id, backlinksShown) {
                return backlinksShown ? "<button type=\"button\" class=\"btn btn-default clear_bg\"  data-bind=\"click:$data.onMinusBacklinkClicked.bind($data,'" + id + "')\"><span class='fa-signal glyphicon glyphicon-arrow-left clear_bg green'></span></button>" : "";
            }

            function getMatchesAddbutton(id, matchesShown, hasMatches) {
                return ((!hasMatches) || (hasMatches && matchesShown)) ? "" : "<button type=\"button\" class=\"btn btn-default clear_bg\" aria-label=\"Left Align\" data-bind=\"click:$data.onPlusMatchesClicked.bind($data,'" + id + "')\"><span class='blue icon-rotated clear_bg glyphicon glyphicon-pause' style='color: #002a80'/></button>";
            }

            function getMatchesMinusButton(id, matchesShown) {
                return matchesShown ? "<button type=\"button\" class=\"btn btn-default clear_bg\"  data-bind=\"click:$data.onMinusMatchesClicked.bind($data,'" + id + "')\"><span class='clear_bg fa-signal icon-rotated glyphicon glyphicon-pause' style='color: #002a80'></span></button>" : "";
            }

            function showPlusButton(id, hasBacklinks, hasMatches, isBackLinkShown, isMatchesShown) {
                if (noPlusButton(hasBacklinks, hasMatches, isBackLinkShown, isMatchesShown)) {
                    return ""
                }
                else {
                    return getBacklinkAddButton(id, isBackLinkShown, hasBacklinks) + getMatchesAddbutton(id, isMatchesShown, hasMatches)
                }
            }

            function showMinusButton(id, isBackLinkShown, isMatchesShown) {
                return (isBackLinkShown || isMatchesShown) ?
                getBacklinkMinusButton(id, isBackLinkShown) + getMatchesMinusButton(id, isMatchesShown) : "";
            }

            var matchingAndBacklinks = container
                .selectAll("." + ko.bindingHandlers.forceGraph.nodeClass)
                .data(graphModel.nodes()).on("mousemove", function (d) {
                    graphModel.d3Layout().stop();
                    var viewBox = container[0][0].viewBox;
                    var x_middle = viewBox.animVal != null ? viewBox.animVal.width / 2 : 0;
                    var y_middle = viewBox.animVal != null ? viewBox.animVal.height / 2 : 0;
                    var iWidth = (d.imageWidth() / 2) * currentScale;
                    var iHeight = (d.imageHeight() / 2) * currentScale;
                    if (d.relType() != 'broken') {
                        tooltip.transition()
                            .duration(200)
                            .style("opacity", 0.8);
                        tooltip.html("<div class=\"dropdown btn-group\" role=\"group\" aria-label=\"\">" +
                                showPlusButton(d.id(), d.hasBacklinks(), d.hasMatches(), d.isBackLinkShown(), d.isMatchesShown()) +
                                showMinusButton(d.id(), d.isBackLinkShown(), d.isMatchesShown()) +
                                "<button type=\"button\" class=\"btn btn-default glyphicon glyphicon-home blue clear_bg\" data-bind=\"click:$data.onNewRootId.bind($data,'" + d.id() + "')\" data-toggle=\"dropdown\" aria-haspopup=\"true\" aria-expanded=\"false\"></button>" +
                                "<button type=\"button\" class=\"btn btn-default glyphicon glyphicon-info-sign blue clear_bg\" data-bind=\"click:$data.onExternalPublish.bind($data,'" + d.id() + "')\" data-toggle=\"dropdown\" aria-haspopup=\"true\" aria-expanded=\"false\"></button>" +
                                "</div>"
                            )
                            .style("left", ((x_middle + iWidth + (d.x - x_middle) * currentScale) + currentXOffset) + "px")
                            .style("top", ((y_middle - iHeight + (d.y - y_middle) * currentScale) + currentYOffset) + "px");
                    }
                    else {
                        tooltip.transition()
                            .duration(10)
                            .style("opacity", 0.8);
                        tooltip.html(
                            "<button type=\"button\" class=\"btn btn-danger clear_bg\" data-toggle=\"dropdown\" aria-haspopup=\"true\" aria-expanded=\"false\"><span class='clear_bg'>Broken node</span></button>"
                            )
                            .style("left", ((x_middle + iWidth + (d.x - x_middle) * currentScale) + currentXOffset) + "px")
                            .style("top", ((y_middle - iHeight + (d.y - y_middle) * currentScale) + currentYOffset) + "px");
                    }
                    ko.applyBindings(viewModel, tooltip[0][0].childNodes[0]);
                });

            container.on("mouseover", function (d) {
                tooltip.transition()
                    .duration(300)
                    .style("opacity", 0);
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
                    var viewBox = container[0][0].viewBox;
                    var x_middle = viewBox.animVal != null ? viewBox.animVal.width / 2 : 0;
                    var y_middle = viewBox.animVal != null ? viewBox.animVal.height / 2 : 0;

                    nodeSelector.attr("transform", function (d) {
                        if (d === nodeSelected) { //Without this, the dragged node jumps out double its dragged distance
                            d.x = nodeSelectedX;
                            d.y = nodeSelectedY;
                        }

                        return "translate(" + ((x_middle + (d.x - x_middle) * currentScale) + currentXOffset)
                            + "," + ((y_middle + (d.y - y_middle) * currentScale) + currentYOffset)
                            + ")scale(" + currentScale + ")";
                    });

                    tooltip.style("opacity", 0);

                    linkSelector.attr("x1", function (d) {
                            return (x_middle + (d.source.x - x_middle) * currentScale) + currentXOffset;
                        })
                        .attr("y1", function (d) {
                            return (y_middle + (d.source.y - y_middle) * currentScale) + currentYOffset;
                        })
                        .attr("x2", function (d) {
                            return (x_middle + (d.target.x - x_middle) * currentScale) + currentXOffset;
                        })
                        .attr("y2", function (d) {
                            return (y_middle + (d.target.y - y_middle) * currentScale) + currentYOffset;
                        });
                });
        }
    };
});
