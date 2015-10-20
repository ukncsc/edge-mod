define([], function () {
    "use strict";

    function hasValue (value) {
        return !!value;
    }

    function isNotEmpty (value) {
        return !!(value && value.trim().length > 0);
    }

    return {
        hasValue: hasValue,
        isNotEmpty: isNotEmpty
    };
});
