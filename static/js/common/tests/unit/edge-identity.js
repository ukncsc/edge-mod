define([
    "intern!object",
    "intern/chai!assert",
    "common/edge-identity"
], function (registerSuite, assert, EdgeIdentity) {
    "use strict";

    var name = "name";
    var name2 = "name2";
    var party_name = "party_name";
    var role = "role";
    var role2 = "role2";
    var language = "language";
    var language2 = "language2";
    var note = "note";
    var note2 = "note2";
    var string = "string";
    var email = "dave@gmail.com";
    var email2 = "dave2@gmail.com";

    var loadFullData = {
        "name": name,
        "roles": [role, role2],
        "specification": {
            "party_name": {
                "name_lines": [
                    {"value": party_name}
                ]
            },
            "languages": [
                {"value": language},
                {"value": language2}
            ],
            "free_text_lines": [
                {"value": note, "type": string},
                {"value": note2, "type": string}
            ],
            "electronic_address_identifiers": [
                {"value": email},
                {"value": email2}
            ]
        }
    };

        var returnObject = {
        "name": name,
        "roles": [role, role2],
        "specification": {
            "party_name": {
                "name_lines": [
                    {"value": party_name, "type": string}
                ]
            },
            "languages": [
                {"value": language},
                {"value": language2}
            ],
            "free_text_lines": [
                {"value": note, "type": string},
                {"value": note2, "type": string}
            ],
            "electronic_address_identifiers": [
                {"value": email},
                {"value": email2}
            ]
        }
    };

    var emptyData = {};


    return registerSuite(function () {

        return {
            name: "common/edge-identity",

            "constructor": function () {
                assert.isDefined(EdgeIdentity);
            },
            "load data": {
                "it will populate the CIQ3.0 Identity from a full data model ": function () {
                    var identity = new EdgeIdentity();

                    //when
                    identity.load(loadFullData);

                    //assert
                    assert.equal(identity.name(), name);
                    assert.equal(identity.party_name(), party_name);
                    assert.deepEqual(identity.roles(), [role, role2]);
                    assert.deepEqual(identity.languages(), [language, language2]);
                    assert.deepEqual(identity.electronic_address_identifiers(), [
                        {"value": email},
                        {"value": email2}
                    ]);
                    assert.deepEqual(identity.free_text_lines(), [note, note2])
                },
                "it will populate the CIQ3.0 Identity with defaults when loading an empty model": function () {
                    var identity = new EdgeIdentity();

                    //when
                    identity.load(emptyData);

                    //assert
                    assert.equal(identity.name(), "");
                    assert.equal(identity.party_name(), "");
                    assert.deepEqual(identity.roles(), []);
                    assert.deepEqual(identity.languages(), []);
                    assert.deepEqual(identity.electronic_address_identifiers(), []);
                    assert.deepEqual(identity.free_text_lines(), [])
                }
            },
            "Field Validation": {
                "it will add another email on addEAddress() if the array is full": function () {
                    var identity = new EdgeIdentity();

                    //when
                    identity.load(loadFullData);

                    //assert
                    assert.equal(identity.electronic_address_identifiers().length, 2);

                    identity.addEAddress();

                    assert.equal(identity.electronic_address_identifiers().length, 3);

                },
                "it wont add another email on addEAddress() if the array isnt full": function () {
                    var identity = new EdgeIdentity();

                    //when
                    identity.load(loadFullData);
                    identity.addEAddress();

                    assert.equal(identity.electronic_address_identifiers().length, 3);

                    identity.addEAddress();

                    assert.equal(identity.electronic_address_identifiers().length, 3);

                }
            },
            "Returning json": {
                "it will return undefined if the identity has no name": function () {
                    var identity = new EdgeIdentity();

                    //when
                    identity.load(emptyData);

                    //assert
                    assert.equal(identity.to_json(), undefined);

                },
                "it will return correct json if the identity has a name": function () {
                    var identity = new EdgeIdentity();

                    //when
                    identity.load(loadFullData);

                    //assert
                    assert.deepEqual(identity.to_json(), loadFullData);

                }
            }
        }
    });
});
