define([], function () {
    "use strict";

    return {
        hasValue: function (value) {
            return !!value;
        },

        isNotEmpty: function (value) {
            return !!(value && value.trim().length > 0);
        }
    };
});
