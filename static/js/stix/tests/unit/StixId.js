define([
    "knockout",
    "intern!object",
    "intern/chai!assert",
    "stix/StixId"
], function (ko, registerSuite, assert, StixId) {
    "use strict";

    // statics go here

    return registerSuite(function () {

        // suite variables go here

        var data = [
            {
                "id_": "certuk:coa-00000000-0000-0000-0000-000000000000",
                "ty": "coa"
            }
        ];

        return {
            name: "stix/StixId",
            "undefined id string": function () {
                assert.throws(
                    function () {
                        new StixId(undefined, data);
                    },
                    "Identifier must be a string"
                );
            },
            "null id string": function () {
                assert.throws(
                    function () {
                        new StixId(null, data);
                    },
                    "Identifier must be a string"
                );
            },
            "non-string id string": function () {
                assert.throws(
                    function () {
                        new StixId(NaN, data);
                    },
                    "Identifier must be a string"
                );
            },
            "invalid id string": function () {
                assert.throws(
                    function () {
                        new StixId("wibble", data);
                    },
                    "Unable to parse id: wibble"
                );
            },
            "valid: type matched": function () {
                var actual = new StixId("certuk:coa-00000000-0000-0000-0000-000000000000", data);
                assert.equal(actual.id(), "certuk:coa-00000000-0000-0000-0000-000000000000");
                assert.equal(actual.type().code, "coa");
                assert.equal(actual.namespace(), "certuk");
            }
        }
    });
})
;
