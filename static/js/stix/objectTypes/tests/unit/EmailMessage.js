define([
    "intern!object",
    "intern/chai!assert",
    "stix/objectTypes/StixObjectType",
    "stix/StixPackage",
    "intern/dojo/text!./data/Observable_package_email.json"
], function (registerSuite, assert, StixObjectType, StixPackage, package01) {
    "use strict";

    // statics go here
    var packageData = Object.freeze({
        "purple-secure-systems:observable-58016966-96f8-4b13-a499-58f57afef616": Object.freeze(JSON.parse(package01))
    });

    return registerSuite(function () {

        // suite variables go here
        var stixPackage = null;
        var classUnderTest = null;

        function loadPackage(rootId) {
            stixPackage = new StixPackage(packageData[rootId], rootId);
            classUnderTest = stixPackage.root;
        }

        return {
            name: "stix/objectTypes/EmailMessage",
            setup: function () {
                loadPackage("purple-secure-systems:observable-58016966-96f8-4b13-a499-58f57afef616");
            },
            "is not null": function () {
                assert.isNotNull(classUnderTest);
            },
            "has correct properties": function () {
                assert.deepEqual(classUnderTest.properties(), [
                    { "label": "From", "value": "\"Lloyds Bank\" <online@lloydsbankv.com>" },
                    { "label": "To", "value": "me@home" },
                    { "label": "Cc", "value": "customers@lloyds.bank" },
                    { "label": "Bcc", "value": "not specified" },
                    { "label": "Subject", "value": "Important Security Alert" },
                    { "label": "Date", "value": "2015-04-21T00:04:25+00:00" },
                    { "label": "Raw Body", "value": "Dear Customer..." }
                ]);
            }
        }
    });
});
