define([
    "dcl/dcl",
    "knockout"
], function (declare, ko) {
    "use strict";

    function createToggleButton(type, glyphicon, state, callback, id) {
        return "<button type=\"button\" class=\"btn btn-default clear_bg\" aria-label=\"Left Align\" data-bind=\"click:$data." + callback + ".bind($data,'" + id + "')\">"
            + "<span class='" + type + " glyphicon glyphicon-" + glyphicon + (state ? " fa-signal " : " ") + "clear_bg'>"
            + "</span>"
            + "</button>";
    }

    function createButton(type, glyphicon, callback, id) {
        return "<button type=\"button\" class=\"btn btn-default clear_bg\" aria-label=\"Left Align\" data-bind=\"click:$data." + callback + ".bind($data,'" + id + "')\">"
            + "<span class='" + type + " glyphicon glyphicon-" + glyphicon + " clear_bg'>"
            + "</span>"
            + "</button>";
    }

    function showMatchesButton(id, hasMatches, matchesShown) {
        return hasMatches ?
            createToggleButton("match icon-rotated", "pause", matchesShown, (matchesShown ? "onMinusMatchesClicked" : "onPlusMatchesClicked"), id)
            : "";
    }

    function showBacklinksButton(id, hasBacklinks, backlinksShown) {
        return hasBacklinks ?
            createToggleButton("backlink", "arrow-left", backlinksShown, (backlinksShown ? "onMinusBacklinkClicked" : "onPlusBacklinkClicked"), id)
            : "";
    }

    function showEdgesButton(id, hasEdges, edgesShown) {
        return hasEdges ?
            createToggleButton("edge", "eye-open", edgesShown, (edgesShown ? "onHideEdges" : "onShowEdges"), id)
            : "";
    }

    function showPublishAndHomeButton(id, nodeType) {
        if (nodeType == 'draft') {
            return "";
        }

        return createButton("", "home", "onNewRootId", id) + createButton("", "info-sign", "onExternalPublish", id);
    }

    return declare(null, {
        declaredClass: "ToolTip",
        constructor: function (tooltip, container, viewModel) {
            this.tooltip = tooltip;
            this.container = container;
            this.viewModel = viewModel;
        },

        hide: function () {
            this.tooltip.transition()
                .duration(300)
                .style("opacity", 0);
        },
        setNodeTooltip: function (d, currentScale, currentXOffset, currentYOffset) {
            var viewBox = this.container.node().viewBox;
            var x_middle = (viewBox.animVal != null ? viewBox.animVal.width / 2 : 0);
            var y_middle = (viewBox.animVal != null ? viewBox.animVal.height / 2 : 0);
            var iWidth = (d.imageWidth() / 4) * currentScale;
            var iHeight = (d.imageHeight() / 4) * currentScale;
            if (d.nodeType() != 'external_ref') {
                this.tooltip.transition()
                    .duration(200)
                    .style("opacity", 0.8);
                this.tooltip.html("<div class=\"btn-group\" role=\"group\" aria-label=\"\">" +
                        showEdgesButton(d.id(), d.hasEdges(), d.isEdgesShown()) +
                        showBacklinksButton(d.id(), d.hasBacklinks(), d.isBackLinkShown()) +
                        showMatchesButton(d.id(), d.hasMatches(), d.isMatchesShown()) +
                        showPublishAndHomeButton(d.id(), d.nodeType()) +
                        "</div>"
                    )
                    .style("left", ((x_middle + iWidth + (d.x - x_middle) * currentScale) + currentXOffset) + "px")
                    .style("top", ((y_middle - iHeight + (d.y - y_middle) * currentScale) + currentYOffset) + "px");
            }
            else {
                this.tooltip.transition()
                    .duration(10)
                    .style("opacity", 0.8);
                this.tooltip.html(
                        "<button type=\"button\" class=\"btn btn-danger clear_bg\" data-toggle=\"dropdown\" aria-haspopup=\"true\" aria-expanded=\"false\">" +
                        "<span class='clear_bg'>External Reference</span>" +
                        "</button>"
                    )
                    .style("left", ((x_middle + iWidth + (d.x - x_middle) * currentScale) + currentXOffset) + "px")
                    .style("top", ((y_middle - iHeight + (d.y - y_middle) * currentScale) + currentYOffset) + "px");
            }
            ko.applyBindings(this.viewModel, this.tooltip.node().childNodes[0]);
        }
    });
});
