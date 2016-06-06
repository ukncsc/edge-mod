define([
    "dcl/dcl",
    "knockout"
], function (declare, ko) {
    "use strict";

    var ICON_ASPECT_RATIO = 1.15;
    var ICON_ROOT_SIZE = 64;
    var ICON_STANDARD_SIZE = 40;

    return declare(null, {
        declaredClass: "Node",
        constructor: function (nodeData) {
            this.id = ko.computed(function () {
                return nodeData.id;
            });
            this.type = ko.computed(function () {
                return nodeData.type;
            });
            this.title = ko.computed(function () {
                return nodeData.title;
            });
            this.depth = ko.computed(function () {
                return nodeData.depth;
            });
            this.relType = ko.computed(function() {
                return nodeData.rel_type;
            });
            this.hasBacklinks = ko.computed(function() {
                return nodeData.has_backlinks;
            });
            this.hasMatches = ko.computed(function() {
                return nodeData.has_matches;
            });
            this.hasEdges = ko.computed(function() {
                return nodeData.has_edges;
            });

            this.isSelected = ko.observable(false);
            this.isChecked = ko.observable(false);

            this.isBackLinkShown = ko.observable(nodeData.backlinks_shown);
            this.isMatchesShown = ko.observable(nodeData.matches_shown);
            this.isEdgesShown = ko.observable(nodeData.edges_shown);

            this.isRelated = ko.observable(false);
            this.className = ko.computed(function () {
                return this.isSelected() ? "selected" : this.isRelated() ? "related" : "unselected";
            }, this);
        },
        isRoot: function () {
            return this.depth() === 0;
        },
        imageHeight: function () {
            return this.isRoot() ? ICON_ROOT_SIZE : ICON_STANDARD_SIZE;
        },
        imageWidth: function () {
            return this.imageHeight() * ICON_ASPECT_RATIO;
        },
        imageX: function () {
            return -(this.imageWidth() / 2);
        },
        imageY: function () {
            return -(this.imageHeight() / 2);
        }
    });
});
