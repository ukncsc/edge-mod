define([
    "dcl/dcl",
    "svg2png"
], function (declare, svg2png) {
    "use strict";

    return declare(null, {
        declaredClass: "PNGConverter",
        constructor: function () {
        },

        getGraph: function (graphID) {
            return document.getElementById((graphID));
        },

        savetoPNG: function (rootID, graphID) {
            svg2png.saveSvgAsPng(this.getGraph(graphID), rootID+".png");
        }

    });
});
