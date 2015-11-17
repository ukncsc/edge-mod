define([
    "dcl/dcl",
    "knockout",
    "./ReviewValue"
], function (declare, ko, ReviewValue) {
    "use strict";

    function flatten(data) {
        var flattened = [];
        var byStateAndMessage = {};
        ko.utils.objectForEach(data, function (id, fields) {
            ko.utils.objectForEach(fields, function (field, validation) {
                //if (validation.status === "ERROR" || validation.status === "WARN") return;
                var state = ReviewValue.State.parse(validation.status);
                var message = validation.message;
                var key = [state, message].join(":");
                var value;
                if (byStateAndMessage.hasOwnProperty(key)) {
                    value = byStateAndMessage[key];
                } else {
                    value = {
                        state: state,
                        message: message,
                        fields: []
                    };
                    byStateAndMessage[key] = value;
                }
                value.fields.push([id, field].join(":"));
            });
        });
        ko.utils.objectForEach(byStateAndMessage, function (key, value) {
            var fieldCount = value.fields.length;
            if (fieldCount > 1) {
                value.message += (" (" + fieldCount + ")");
            }
            flattened.push(ko.observable(value));
        });
        return ko.observableArray(flattened);
    }

    return declare(null, {
        declaredClass: "ValidationInfo",
        constructor: function (validationInfo) {
            this._data = validationInfo || {};
            var flattened = flatten(this._data);
            this.hasMessages = ko.computed(function () {
                return flattened().length > 0;
            });
            this.errors = ko.computed(function () {
                return ko.utils.arrayFilter(flattened(), function (item) {
                    return item().state === ReviewValue.State.ERROR;
                });
            }, this);
            this.hasErrors = ko.computed(function () {
                return this.errors().length > 0;
            }, this);
            this.warnings = ko.computed(function () {
                return ko.utils.arrayFilter(flattened(), function (item) {
                    return item().state === ReviewValue.State.WARN;
                });
            }, this);
            this.hasWarnings = ko.computed(function () {
                return this.warnings().length > 0;
            }, this);
            this.infos = ko.computed(function () {
                return ko.utils.arrayFilter(flattened(), function (item) {
                    return item().state === ReviewValue.State.INFO;
                });
            }, this);
            this.hasInfos = ko.computed(function () {
                return this.infos().length > 0;
            }, this);
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
