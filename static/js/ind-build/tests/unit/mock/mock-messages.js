define([
    "knockout",
    "../../../../dcl/dcl"
], function (ko, declare) {
    "use strict";

    return declare(null, {
        declaredClass: "Messages",

        constructor: function () {
            this.errors = ko.observableArray([]);
        },

        addError: function (message) {
            this.errors.push(message);
        },

        hasErrors: function () {
            return this.errors().length > 0;
        }
    })
});

