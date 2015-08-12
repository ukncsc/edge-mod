define([
    "dcl/dcl",
    "knockout",
    "./Modal"
], function (declare, ko, Modal) {
    "use strict";

    return declare(Modal, {
        constructor: function (options) {
            this.titleIcon = options["titleIcon"] || "glyphicon-question-sign";

            this.buttonData([
                {
                    label: options["isYesNo"] ? "Yes" : "OK",
                    icon: options["showIcons"] ? "glyphicon-ok" : "",
                    callback: options["onConfirm"]
                },
                {
                    label: options["isYesNo"] ? "No" : "Cancel",
                    icon: options["showIcons"] ? "glyphicon-remove" : ""
                }
            ]);
        }
    });
});
