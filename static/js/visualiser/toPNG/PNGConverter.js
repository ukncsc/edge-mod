define([
    "knockout",
    "svg2png"
], function (ko, svg2png) {
    "use strict";

    return {
        getSVG: function (buttonElement) {
            return buttonElement.currentTarget.parentNode.parentNode.children["visualiser-graph"]
        },

        savetoPNG: function (buttonElement, rootID) {
            svg2png.saveSvgAsPng(this.getSVG(buttonElement).cloneNode(true), rootID + ".png");
        }
    }
});
