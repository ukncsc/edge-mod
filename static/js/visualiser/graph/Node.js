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
            this.id = ko.observable(nodeData.id);
            this.type = ko.observable(nodeData.type);
            this.title = ko.observable(nodeData.title);
            this.depth = ko.observable(nodeData.depth);
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
