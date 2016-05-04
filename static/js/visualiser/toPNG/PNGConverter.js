define([
    "dcl/dcl",
    "svg2png"
], function (declare, svg2png) {
    "use strict";

    return declare(null, {
        declaredClass: "PNGConverter",
        constructor: function () {
        },

        getGraph: function () {
            return document.getElementById(("visualiser-graph"));
        },

        savetoPNG: function (rootID) {
            svg2png.saveSvgAsPng(this.getGraph(), rootID+".png");
        }

    });
});
