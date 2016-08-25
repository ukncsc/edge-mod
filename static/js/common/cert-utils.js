define([], function () {
    "use strict";

    return Object.freeze({
        checkNestedFieldExists: function (obj /*, level1, level2, ... levelN*/) {
            var args = Array.prototype.slice.call(arguments, 1);

            for (var i = 0; i < args.length; i++) {
                if (!obj || !obj.hasOwnProperty(args[i])) {
                    return false;
                }
                obj = obj[args[i]];
            }
            return true;
        },
        checkNestedFieldExistsArray: function (obj,/*Array*/ args) {
            for (var i = 0; i < args.length; i++) {
                if (!obj || !obj.hasOwnProperty(args[i])) {
                    return false;
                }
                obj = obj[args[i]];
            }
            return true;
        },
        getNestedFieldArray: function (obj, /*Array*/args) {
            var currentLevel = obj;
            for (var i = 0; i < args.length; i++) {
                currentLevel = currentLevel[args[i]];
            }
            return currentLevel;
        }
    });
});
