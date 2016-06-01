define([
    "knockout",
    "svg2png"
], function (ko, svg2png) {
    "use strict";

    return {
        getSiblingSVG: function (buttonElement) {
            return buttonElement.currentTarget.parentNode.children["visualiser-graph"]
        },

        savetoPNG: function (buttonElement, rootID) {
            svg2png.saveSvgAsPng(this.getSiblingSVG(buttonElement), rootID + ".png");
        }
    }
});
