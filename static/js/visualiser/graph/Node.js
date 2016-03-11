define([
    "dcl/dcl",
    "knockout"
], function (declare, ko) {
    "use strict";

    // icon sizes
    var aspectRatio = 1.15;
    var root = 64;
    var standard = 40;

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
            this.isSelected = ko.observable(false);
            this.className = ko.computed(function () {
                return this.isSelected() ? "selected" : "unselected";
            }, this);
        },
        isRoot: function () {
            return this.depth() === 0;
        },
        imageHeight: function () {
            return this.isRoot() ? root : standard;
        },
        imageWidth: function () {
            return this.imageHeight() * aspectRatio;
        },
        imageX: function () {
            return -(this.imageWidth() / 2);
        },
        imageY: function () {
            return -(this.imageHeight() / 2);
        }
    });
});
