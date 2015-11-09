define([
    "intern!object",
    "intern/chai!assert",
    "knockout",
    "stix/ValidationInfo"
], function (registerSuite, assert, ko, ValidationInfo) {
    "use strict";

    // statics go here
    var validationInfo = Object.freeze({
        "id1": {
            "field1": {
                "status": "ERROR",
                "message": "Bad input"
            },
            "field2": {
                "status": "WARN",
                "message": "May have expired"
            },
            "field3": {
                "status": "WARN",
                "message": "Will expire soon"
            }
        },
        "id2": {
            "field4": {
                "status": "ERROR",
                "message": "Bad input"
            },
            "field5": {
                "status": "INFO",
                "message": "Missing value"
            }
        }
    });

    return registerSuite(function () {

        // suite variables go here
        var classUnderTest = null;

        return {
            name: "ValidationInfo",
            "constructor: no data": {
                setup: function () {
                    classUnderTest = new ValidationInfo();
                },
                "hasMessages() is false": function() {
                    assert.isFalse(classUnderTest.hasMessages());
                },
                "errors() is empty array": function () {
                    assert.deepEqual(classUnderTest.errors(), []);
                },
                "hasErrors() is false": function() {
                    assert.isFalse(classUnderTest.hasErrors());
                },
                "warnings() is empty array": function () {
                    assert.deepEqual(classUnderTest.warnings(), []);
                },
                "hasWarnings() is false": function() {
                    assert.isFalse(classUnderTest.hasWarnings());
                },
                "infos() is empty array": function () {
                    assert.deepEqual(classUnderTest.infos(), []);
                },
                "hasInfos() is false": function () {
                    assert.isFalse(classUnderTest.hasInfos());
                },
                "findByProperty() returns OK/null": function () {
                    assert.deepEqual(classUnderTest.findByProperty("any", "any"), {
                        "state": 0,
                        "message": null
                    })
                }
            },
            "constructor: with data": {
                setup: function () {
                    classUnderTest = new ValidationInfo(validationInfo);
                },
                "hasMessages() is true": function() {
                    assert.isTrue(classUnderTest.hasMessages());
                },
                "errors() has 2 errors": function () {
                    assert.deepEqual(ko.toJS(classUnderTest.errors()), [{
                        "fields": [
                            "id1:field1",
                            "id2:field4"
                        ],
                        "message": "Bad input (2)",
                        "state": 3
                    }]);
                },
                "hasErrors() is true": function() {
                    assert.isTrue(classUnderTest.hasErrors());
                },
                "warnings() has 2 warnings": function () {
                    assert.deepEqual(ko.toJS(classUnderTest.warnings()), [{
                        "fields": [
                            "id1:field2"
                        ],
                        "message": "May have expired",
                        "state": 2
                    },{
                        "fields": [
                            "id1:field3"
                        ],
                        "message": "Will expire soon",
                        "state": 2
                    }]);
                },
                "hasWarnings() is true": function() {
                    assert.isTrue(classUnderTest.hasWarnings());
                },
                "infos() has 1 info": function () {
                    assert.deepEqual(ko.toJS(classUnderTest.infos()), [{
                        "fields": [
                            "id2:field5"
                        ],
                        "message": "Missing value",
                        "state": 1
                    }]);
                },
                "hasInfos() is true": function() {
                    assert.isTrue(classUnderTest.hasInfos());
                },
                "findByProperty() returns status/message": function () {
                    assert.deepEqual(classUnderTest.findByProperty("id1", "field3"), {
                        "state": 2,
                        "message": "Will expire soon"
                    })
                }
            }
        }
    });
});
