// We've separated the (global) functions

// This is copy and pasted everywhere. This should be included once (e.g. in the base.html template)...
define([
    "knockout"
], function (ko) {
    "use strict";

    return {
        changeTracker: function (objectToTrack, hashFunction) {
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
        },

        inherit: function (proto) {
            var F = function F() {
            };
            F.prototype = proto;
            return new F();
        },

        extend: function (child, parent) {
            child.prototype = this.inherit(parent.prototype);
            child.prototype.constructor = child;
            child.super = parent.prototype;
        }
    };
});