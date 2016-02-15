define([
    "../dcl/dcl",
    "knockout"
], function (declare, ko) {
    "use strict";

    function BuildMode() {
        this.value = ko.observable(
            BuildMode.prototype.MODES.CREATE
        );
    }

    BuildMode.prototype.MODES = Object.freeze({
        CREATE: "Build",
        EDIT: "Edit",
        VIEW: "View"
    });

    BuildMode.prototype.isEditable = function () {
        var currentValue = this.value();
        return currentValue === BuildMode.prototype.MODES.CREATE
            || currentValue === BuildMode.prototype.MODES.EDIT;
    };

    BuildMode.prototype.isReadOnly = function () {
        return !this.isEditable();
    };

    BuildMode.prototype.isNew = function () {
        return this.value() === BuildMode.prototype.MODES.CREATE;
    };

    return  BuildMode;
});
