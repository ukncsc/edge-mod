define([
    "dcl/dcl",
    "knockout",
    "./Modal"
], function (declare, ko, Modal) {
    "use strict";

    return declare(Modal, {
        constructor: function (options) {
            this.buttonData([
                {
                    label: "OK",
                    icon: options["showIcons"] ? "glyphicon-ok" : "",
                    callback: options["onConfirm"]
                },
                {
                    label: "Cancel",
                    icon: options["showIcons"] ? "glyphicon-remove" : ""
                }
            ]);
        }
    });
});
