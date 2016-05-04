define([
    "dcl/dcl",
    "knockout",
    "svg2png"
], function (declare, ko, svg2png) {
    "use strict";

    return declare(null, {
        declaredClass: "PNGConverter",
        constructor: function (graphID) {
            this.graphID = ko.computed(function () {
                return graphID;
            });
        },

        getGraph: function () {
            return document.getElementById((this.graphID()));
        },

        savetoPNG: function (rootID) {
            svg2png.saveSvgAsPng(this.getGraph(), rootID + ".png");
        }

    });
});
