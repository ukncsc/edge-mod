define([
    "intern!object",
    "intern/chai!assert",
    "knockout",
    "common/change-tracker"
], function (registerSuite, assert, ko, ChangeTracker) {
    "use strict";

    // statics go here

    return registerSuite(function () {

        // suite variables go here

        return {
            name: "common/change-tracker",
            "ko.ignoreComputeHash": {
                "isTrue": function () {
                    assert.isTrue(ko.ignoreComputeHash({ignoreComputeHash: true}));
                },
                "isFalse": function () {
                    assert.isFalse(ko.ignoreComputeHash({}));
                    assert.isFalse(ko.ignoreComputeHash({ignoreComputeHash: 0}));
                    assert.isFalse(ko.ignoreComputeHash({ignoreComputeHash: "true"}));
                }
            },
            "ko.hasCustomHash": {
                "has custom hash": function () {
                    assert.isTrue(ko.hasCustomHash({
                        customHash: ko.computed(function () {
                        })
                    }));
                },
                "does not have custom hash": function () {
                    assert.isFalse(ko.hasCustomHash({}));
                    assert.isFalse(ko.hasCustomHash({
                        customHash: ko.observable()
                    }));
                }
            },
            "ko.extenders.customHash": {
                "not specified": function () {
                    var actual = ko.extenders.customHash({}, {});
                    assert.isNotFunction(actual.customHash);
                },
                "specified": function () {
                    var actual = ko.extenders.customHash({}, {
                        computeHashCallback: function () {
                        }
                    });
                    assert.isFunction(actual.customHash);
                    assert.isTrue(ko.isComputed(actual.customHash));
                }
            },
            "ko.extenders.cachedArrayHash": {
                "not specified": function () {
                    var actual = ko.extenders.cachedArrayHash({});
                    assert.isUndefined(actual._hashResults);
                },
                "specified on non-array": function () {
                    var actual = ko.extenders.cachedArrayHash(ko.observable({}), true);
                    assert.isUndefined(actual._hashResults);
                },
                "specified": function () {
                    var actual = ko.extenders.cachedArrayHash(ko.observableArray([]), true);
                    assert.isDefined(actual._hashResults);
                },
                "specified: hashes are as expected": function () {
                    var actual = ko.extenders.cachedArrayHash(ko.observableArray([]), true);
                    assert.isDefined(actual._hashResults);
                    actual.push("Curly", "Larry", "Moe");
                    actual.push("Tic", "Tac", "Toe");
                    actual.pop();
                    actual.shift();
                    actual.reverse();
                    var actualHashes = actual._hashResults.peek();
                    assert.deepEqual(actualHashes, [
                        ChangeTracker.hashCode("Tac"),
                        ChangeTracker.hashCode("Tic"),
                        ChangeTracker.hashCode("Moe"),
                        ChangeTracker.hashCode("Larry")
                    ]);
                }
            },
            "ko.extenders.ignoreComputeHash": {
                "not specified": function () {
                    var actual = ko.extenders.ignoreComputeHash({});
                    assert.isFalse(actual.ignoreComputeHash);
                },
                "specified": function () {
                    var actual = ko.extenders.ignoreComputeHash({}, true);
                    assert.isTrue(actual.ignoreComputeHash);
                }
            },
            "ChangeTracker.create()": {
                "with default hash function": function () {
                    var objectToTrack = ko.observable("42");
                    var actual = ChangeTracker.create(objectToTrack);
                    assert.instanceOf(actual(), ChangeTracker);
                    objectToTrack("999");
                    assert.isTrue(actual().somethingHasChanged());
                    actual().markCurrentStateAsClean();
                    assert.isFalse(actual().somethingHasChanged());
                },
                "with specified hash function": function () {
                    var actual = ChangeTracker.create(ko.observable("42"), function () {
                        return 42;
                    });
                    assert.instanceOf(actual(), ChangeTracker);
                }
            },
            "ChangeTracker.hashCode()": {
                "function": function () {
                    assert.isNull(ChangeTracker.hashCode(function () {
                    }));
                },
                "observable: computed": function () {
                    assert.isNull(ChangeTracker.hashCode(ko.computed(function () {
                    })));
                },
                "observable: ignoreComputeHash": function () {
                    assert.isNull(ChangeTracker.hashCode(ko.observable().extend({
                        ignoreComputeHash: true
                    })));
                },
                "observable: custom hash": function () {
                    var observable = ko.observable("").extend({
                        customHash: {
                            computeHashCallback: function () {
                                return 42;
                            }
                        }
                    });
                    var actual = ChangeTracker.hashCode(observable);
                    assert.equal(actual, 42);
                },
                "observable: default hash": function () {
                    assert.equal(ChangeTracker.hashCode(ko.observable("42")), 1662);
                },
                "boolean: true": function () {
                    assert.equal(ChangeTracker.hashCode(ko.observable(true)), 1);
                },
                "boolean: false": function () {
                    assert.equal(ChangeTracker.hashCode(ko.observable(false)), 0);
                },
                "date: invalid": function () {
                    assert.equal(ChangeTracker.hashCode(ko.observable(new Date(NaN))), 0);
                },
                "date: valid": function () {
                    assert.equal(ChangeTracker.hashCode(ko.observable(new Date(Date.UTC(2015, 10, 17)))), 1447718400000);
                },
                "number: not finite": function () {
                    assert.equal(ChangeTracker.hashCode(ko.observable(Infinity)), 0);
                    assert.equal(ChangeTracker.hashCode(ko.observable(NaN)), 0);
                },
                "number: finite": function () {
                    assert.equal(ChangeTracker.hashCode(ko.observable(42)), 42);
                },
                "string: empty": function () {
                    assert.equal(ChangeTracker.hashCode(ko.observable("")), 0);
                },
                "string: 1 character": function () {
                    assert.equal(ChangeTracker.hashCode(ko.observable("X")), 88);
                },
                "string: multiple characters": function () {
                    assert.equal(ChangeTracker.hashCode(ko.observable("Curly, Larry and Moe")), 654150973);
                },
                "array: empty": function () {
                    assert.equal(ChangeTracker.hashCode(ko.observable([])), 0);
                },
                "array: 1 non-hashable item": function () {
                    assert.equal(ChangeTracker.hashCode(ko.observable([function(){}])), 0);
                },
                "array: 1 item": function () {
                    assert.equal(ChangeTracker.hashCode(ko.observable(["Curly, Larry and Moe"])), 654150973);
                },
                "array: multiple items": function () {
                    assert.equal(ChangeTracker.hashCode(ko.observable(["Curly", "Larry", "Moe"])), 765446988);
                },
                "object: empty": function () {
                    assert.equal(ChangeTracker.hashCode(ko.observable({})), 0);
                },
                "object: hashable items": function () {
                    assert.equal(ChangeTracker.hashCode(ko.observable({"Curly": "tic", "Larry": "tac", "Moe": "toe"})), -1926928458);
                },
                "null": function () {
                    assert.equal(ChangeTracker.hashCode(null), 0);
                },
                "undefined": function () {
                    assert.equal(ChangeTracker.hashCode(undefined), 0);
                }
            }
        }
    });
});
