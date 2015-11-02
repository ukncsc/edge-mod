define([
    "dcl/dcl",
    "./ReviewValue"
], function (declare, ReviewValue) {
    "use strict";

    return declare(null, {
        declaredClass: "ValidationInfo",
        constructor: function (validationInfo) {
            this._data = validationInfo;
        },

        findByProperty: function (/*String*/ id, /*String*/ propertyPath) {
            var val = (this._data[id] || {})[propertyPath];
            return {
                "state": val && ReviewValue.State.parse(val.status) || ReviewValue.State.OK,
                "message": val && val.message || null
            };
        }
    });
});
