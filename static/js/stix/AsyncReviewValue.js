define([
    "dcl/dcl",
    "knockout",
    "./ReviewValue"
], function (declare, ko, ReviewValue) {
    "use strict";

    return declare(ReviewValue, {
        declaredClass: "AsyncReviewValue",
        constructor: declare.superCall(function (sup) {
            return function (/*Any*/ value, /*State?*/ state, /*String?*/ message) {
                if (ko.isObservable(value)) {
                    this.value = ko.computed(function () {
                        return value();
                    });

                    this.isEmpty = ko.computed(function () {
                        return this.value() === null;
                    }.bind(this));
                }
            }
        })
    });
});
