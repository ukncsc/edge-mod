define([
    "knockout",
    "dcl/dcl"
], function (ko, declare) {
    "use strict";

    return declare(null, {
        declaredClass: "BuildMode",

        MODES: Object.freeze({
            CREATE: "Build",
            EDIT: "Edit",
            VIEW: "View"
        }),

        constructor: function BuildMode() {
            this.value = ko.observable(
                this.MODES.CREATE
            );
        },

        isEditable: function () {
            var currentValue = this.value();
            return currentValue === this.MODES.CREATE
                || currentValue === this.MODES.EDIT;
        },

        isReadOnly: function () {
            return !this.isEditable();
        },

        isNew: function () {
            return this.value() === this.MODES.CREATE;
        }
    });
});
