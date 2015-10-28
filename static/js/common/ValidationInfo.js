define([
    "dcl/dcl",
    "./ValidationStatus"
], function (declare, ValidationStatus) {
    "use strict";

    return declare(null, {
        declaredClass: "ValidationInfo",
        constructor: function (params) {
            var validationParams = params || {};
            this.status = ValidationStatus[validationParams.status] || ValidationStatus.OK;
            this.message = validationParams.message;
        }
    });
});
