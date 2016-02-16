// We've separated the (global) functions

// This is copy and pasted everywhere. This should be included once (e.g. in the base.html template)...
define([
    "../dcl/dcl",
    "knockout"
], function (declare, ko) {
    "use strict";

    function MiscFunctions(){};

    MiscFunctions.changeTracker = function(objectToTrack, hashFunction) {
        // https://github.com/knockout/knockout/wiki/Dirty-tracking
        hashFunction = hashFunction || ko.toJSON;
        var lastCleanState = ko.observable(hashFunction(objectToTrack));

        var result = {
            somethingHasChanged: ko.dependentObservable(function () {
                return hashFunction(objectToTrack) != lastCleanState()
            }),
            markCurrentStateAsClean: function () {
                lastCleanState(hashFunction(objectToTrack));
            }
        };

        return function () {
            return result
        }
    }


    MiscFunctions.getField = function(obj, key) {
        return key.split(".").reduce(function(o,x) {
            return (typeof o == "undefined" || o === null) ? o : o[x];
        }, obj);
    }

    // use to find if array contains an item, is called by
    // contains.call(myArray, value)
    MiscFunctions.contains = function(needle) {
        // Per spec, the way to identify NaN is that it is not equal to itself
        var findNaN = needle !== needle;
        var indexOf;

        if(!findNaN && typeof Array.prototype.indexOf === 'function') {
            indexOf = Array.prototype.indexOf;
        } else {
            indexOf = function(needle) {
                var i = -1, index = -1;

                for(i = 0; i < this.length; i++) {
                    var item = this[i];

                    if((findNaN && item !== item) || item === needle) {
                        index = i;
                        break;
                    }
                }

                return index;
            };
        }
        return indexOf.call(this, needle) > -1;
    }

    MiscFunctions.fullArray = function (arr) {
        if(arr.length === 0){
            return true
        }
        for(var i = 0; i<arr.length; i++){
            var item = arr[i].trim();

            if(item.length === 0 || !item) {
                return false
            }
        }
        return true
    }

    MiscFunctions.arrayisFull = function (arr) {
        return MiscFunctions.fullArray(arr);
    }

    MiscFunctions.arrayHasEmptyEmailAddresses = function (arr) {
         return MiscFunctions.contains.call(arr,{value: '', type: ''});
    }

    MiscFunctions.inherit = function(proto) {
        var F = function F() {
        };
        F.prototype = proto;
        return new F();
    }

    MiscFunctions.extend = function(child, parent) {
        child.prototype = MiscFunctions.inherit(parent.prototype);
        child.prototype.constructor = child;
        child.super = parent.prototype;
    }

    ko.onDemandObservable = function (callback, target) {
        // Perhaps pass this in, making this function a wrapper on existing observables..?
        var _value = ko.observableArray();

        var result = ko.computed({
            read: function () {
                if (!result.loaded()) {
                    callback.call(target);
                }

                return _value();
            },
            write: function (newValue) {
                result.loaded(true);
                _value(newValue);
            },
            deferEvaluation: true
        });

        result.loaded = ko.observable();
        // Could make this a computed observable, so it would refresh automatically?
        result.refresh = function () {
            result.loaded(false);
        };

        return result;
    };

    ko.bindingHandlers.effectOnChange = {
        update: function (element, valueAccessor, allBindings) {
            var value = valueAccessor();
            var applyEffectOnEmpty = allBindings.get('applyEffectOnEmpty') === 'true';
            if (applyEffectOnEmpty || ko.unwrap(value)) {
                var effect = allBindings.get('effectName') || 'shake';
                $(element).effect(effect);
            }
        }
    };

    ko.bindingHandlers.highlightedText = {
        update: function (element, valueAccessor) {
            var options = valueAccessor();
            var search = ko.utils.unwrapObservable(options.match);
            search = search.trim().replace(/\s/g, "|");
            search = "\\b(" + search + ")\\b";
            var value = ko.utils.unwrapObservable(options.text);
            var css = ko.utils.unwrapObservable(options.css);
            element.innerHTML = value.replace(new RegExp(search, 'gi'), '<span class="' + css + '">' + '$&' + '</span>');
        }
    };

    ko.extenders.validate = function (target, options) {
        var isValidCallback = options['isValidCallback'];
        var failedValidationMessage = options['failedValidationMessage'];
        target.hasError = ko.observable(false);
        target.errorMessage = ko.observable("");
        target.hasValidation = true;

        function validate() {
            var isValid = isValidCallback(target());

            target.hasError(!isValid);
            target.errorMessage(isValid ? "" : failedValidationMessage);
        }

        target.subscribe(validate);

        return target;
    };

    ko.extenders.required = function (target, required) {
        if (required === true) {
            return ko.extenders.validate(target, {
                isValidCallback: function (value) {
                    return (typeof value === "string" && value.trim().length > 0) || isFinite(parseFloat(value));
                },
                failedValidationMessage: "* (Required)"
            });
        }
        return target;
    };


    return MiscFunctions;
});

/*
(function (ko) {
    var existing = ko.bindingProvider.instance;
    ko.bindingProvider.instance = {
        nodeHasBindings: existing.nodeHasBindings,
        getBindings: function (node, bindingContext) {
            var bindings;
            try {
                bindings = existing.getBindings(node, bindingContext);
            } catch (ex) {
                if (window.console && console.log) {
                    console.log("binding error", ex.message, node, bindingContext);
                }
            }
            return bindings;
        }
    };
})(ko);
*/
