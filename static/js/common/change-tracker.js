define([
    "dcl/dcl",
    "knockout"
], function (declare, ko) {
    "use strict";

    ko.ignoreComputeHash = function (obj) {
        return obj.ignoreComputeHash === true;
    };

    ko.hasCustomHash = function (obj) {
        return ko.isComputed(obj.customHash);
    };

    ko.extenders.customHash = function (target, options) {
        var computeHashCallback = options["computeHashCallback"];
        if (typeof computeHashCallback === "function") {
            target.customHash = ko.computed(computeHashCallback);
        }

        return target;
    };

    ko.extenders.cachedArrayHash = function (target, options) {
        if (options === true && target.peek() instanceof Array) {
            target._hashResults = ko.observableArray([]);

            target.subscribe(function (changes) {
                var numChanges = changes.length;
                var underlyingHashResults = target._hashResults.peek();

                function allChangesAreAdd(changes) {
                    for (var i = 0, allChanges = true, numChanges = changes.length; i < numChanges; ++i) {
                        allChanges = changes["status"] === "added";
                    }
                    return allChanges;
                }

                function generateElementHash(element) {
                    return ChangeTracker.hashCode(element);
                }

                if (underlyingHashResults.length === 0 || allChangesAreAdd(changes)) {
                    underlyingHashResults.push.apply(underlyingHashResults, changes.map(function (currentChange) {
                        return generateElementHash(currentChange["value"]);
                    }));
                } else {
                    for (var i = 0; i < numChanges; ++i) {
                        var changeInfo = changes[i];
                        var element = changeInfo["value"];
                        if (changeInfo["status"] === "added") {
                            underlyingHashResults.splice(changeInfo["index"], 0, generateElementHash(element));
                        } else { // if (changeInfo["status"] === "deleted") {
                            underlyingHashResults.splice(changeInfo["index"], 1);
                        }
                    }
                }

                // Now we can notify...
                target._hashResults.valueHasMutated();
            }, null, "arrayChange");

            return ko.extenders.customHash(target, {
                "computeHashCallback": function () {
                    return ChangeTracker.hashCode(target._hashResults());
                }
            });
        }

        return target;
    };

    ko.extenders.ignoreComputeHash = function (target, options) {
        target.ignoreComputeHash = options === true;
        return target;
    };

    var _hashFunctions = Object.freeze({
        "Function": function (obj) {
            var h = null;
            if (ko.isObservable(obj)) {
                if (ko.isComputed(obj) || ko.ignoreComputeHash(obj)) {
                    // ignored
                } else if (ko.hasCustomHash(obj)) {
                    h = obj.customHash();
                } else {
                    h = ChangeTracker.hashCode(obj());
                }
            }
            return h;
        },
        "Boolean": function (obj) {
            return obj ? 1 : 0;
        },
        "Date": function (obj) {
            return obj.getTime() || 0;
        },
        "Number": function (obj) {
            return isFinite(obj) ? obj : 0;
        },
        "String": function (obj) {
            var h = 0;
            for (var i = 0, len = obj.length; i < len; i++) {
                h = ((h << 5) - h) + obj.charCodeAt(i);
                h |= 0;
            }
            return h;
        },
        "Array": function (obj) {
            var h = 0;
            for (var i = 0, len = obj.length; i < len; i++) {
                var hc = ChangeTracker.hashCode(obj[i]);
                if (typeof hc === "number") {
                    h = ((h << 5) - h) + hc;
                    h |= 0;
                }
            }
            return h;
        },
        "Object": function (obj) {
            var h = 0;
            Object.keys(obj).sort().forEach(function (key) {
                var hc = ChangeTracker.hashCode([key, obj[key]]);
                h = ((h << 5) - h) + hc;
                h |= 0;
            });
            return h;
        }
    });

    function _defaultHashFunction() {
        return 0;
    }

    var ChangeTracker = declare(null, {
        declaredClass: "ChangeTracker",
        constructor: function (objectToTrack, hashFunction) {
            var lastCleanState = ko.observable(hashFunction(objectToTrack));

            this.somethingHasChanged = ko.computed(function () {
                return hashFunction(objectToTrack) != lastCleanState()
            });
            this.markCurrentStateAsClean = function () {
                lastCleanState(hashFunction(objectToTrack));
            };
        }
    });

    ChangeTracker.create = function (objectToTrack, hashFunction) {
        var tracker = new ChangeTracker(objectToTrack, hashFunction || ChangeTracker.hashCode);
        return function() {
            return tracker;
        }
    };

    ChangeTracker.hashCode = function (obj) {
        var objectType = Object.prototype.toString.call(obj).slice(8, -1);
        return (_hashFunctions[objectType] || _defaultHashFunction)(obj);
    };

    return ChangeTracker;
});
