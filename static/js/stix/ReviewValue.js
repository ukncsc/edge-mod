define([
    "dcl/dcl",
    "knockout"
], function (declare, ko) {
    "use strict";

    function capitalise(str) {
        return str.charAt(0).toUpperCase() + str.slice(1).toLowerCase();
    }
    function uncamel(str) {
        return str.replace(/(^|[A-Z])/g, " $1");
    }

    var valueBuilders = Object.freeze({
        "Boolean" : function (rawValue) {
            return rawValue;
        },
        "Number" : function (rawValue) {
            return isFinite(rawValue) ? rawValue : null;
        },
        "String" : function (rawValue) {
            return rawValue.length > 0 ? rawValue : null;
        },
        "Array" : function (rawValue) {
            return rawValue.length > 0
                ? rawValue.slice(0, -1).join(", ") + " and " + rawValue[rawValue.length - 1]
                : null;
        },
        "Object" : function (rawValue) {
            var condition = rawValue["condition"] || "Equals";
            var applyCondition = rawValue["apply_condition"];
            var value = buildValue(rawValue["value"]);
            if (value != null) {
                var builtValue = [];
                if (applyCondition) {
                    builtValue.push(capitalise(applyCondition));
                }
                if (condition && condition !== "Equals") {
                    builtValue.push(uncamel(condition));
                }
                builtValue.push(value);
                return builtValue.join(" ");
            }
            return null;
        }
    });

    function defaultValueBuilder (rawValue) {
        return rawValue ? String(rawValue) : null;
    }

    function buildValue(rawValue) {
        var valueType = Object.prototype.toString.call(rawValue).slice(8, -1);
        return (valueBuilders[valueType] || defaultValueBuilder)(rawValue);
    }

    function isValidState(state) {
        return isFinite(state) && state >= ReviewValue.State.OK && state <= ReviewValue.State.ERROR;
    }

    var ReviewValue = declare(null, {
        declaredClass: "ReviewValue",
        constructor: function (/*Any*/ value, /*State?*/ state, /*String?*/ message) {
            this.value = ko.computed(function () {
                return buildValue(value);
            });
            this.state = ko.computed(function () {
                return isValidState(state) ? state : ReviewValue.State.OK;
            });
            this.message = ko.computed(function () {
                return this.state() === ReviewValue.State.OK ? null : message || null;
            }.bind(this));

            this.hasValue = ko.computed(function () {
                return this.value() !== null;
            }.bind(this));
            this.hasError = ko.computed(function () {
                return this.state() === ReviewValue.State.ERROR;
            }.bind(this));
            this.hasWarning = ko.computed(function () {
                return this.state() === ReviewValue.State.WARN;
            }.bind(this));
            this.hasInfo = ko.computed(function () {
                return this.state() === ReviewValue.State.INFO;
            }.bind(this));
        }
    });
    ReviewValue.State = Object.freeze({
        parse: function (stateString) {
            var state = ReviewValue.State[stateString];
            if (isValidState(state)) {
                return state;
            } else {
                throw new Error("Invalid state: " + stateString);
            }
        },
        OK: 0,
        INFO: 1,
        WARN: 2,
        ERROR: 3
    });
    return ReviewValue;
});
