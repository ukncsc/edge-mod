define([
    "intern!object",
    "intern/chai!assert",
    "common/mock-stickytape",
    "common/identity"
], function (registerSuite, assert, mstickytape, Identity) {
    "use strict";

    var testORG = 'test-org';
    var testORG2 = 'test-org2';
    var uuid = '54163ff2-9431-4eb0-a4ea-5e41500d30d4';
    var it = 'IT';

    var crmKBData = {
        name: uuid,
        roles: null,
        specification: {
            organisation_info: it
        }
    };

    var externalkBData = {
        name: testORG2,
        roles: null,
        specification: {
            organisation_info: it
        }
    };

    return registerSuite(function () {

        return {
            name: "common/identity",

            "constructor": function () {
                assert.isDefined(Identity);
            },
            "load data": {
                "it will populate non-crm identities names and UUID's with the CIQ Identity name": function () {
                    var identity = new Identity();

                    //given
                    getJSONReturnError = false;

                    //when
                    identity.load(externalkBData);

                    //assert
                    assert.equal(identity.sector(), it);
                    assert.equal(identity.UUID(), testORG2);
                    assert.equal(identity.name(), testORG2);
                },
                "it will load crm identities correctly, fetching the name using the UUID stored in the CIQ name": function () {
                    var identity = new Identity();

                    //given
                    getJSONReturnError = false;

                    //when
                    identity.load(crmKBData);

                    //assert
                    assert.equal(identity.sector(), it);
                    assert.equal(identity.UUID(), uuid);
                    assert.equal(identity.name(), testORG);
                },
                "Identity name will default to UUID if can't retrieve from CRM ": function () {
                    var identity = new Identity();

                    //given
                    getJSONReturnError = true;

                    //when
                    identity.load(crmKBData);

                    //assert
                    assert.equal(identity.sector(), it);
                    assert.equal(identity.UUID(), uuid);
                    assert.equal(identity.name(), uuid);
                }
            },
           "return json": {
                 "to_json will return the correct data": function () {
                    var identity = new Identity();

                    //given
                    getJSONReturnError = false;

                    //when
                    identity.load(externalkBData);

                    var json = identity.to_json();

                    var expectedJson = {
                        name: testORG2,
                        specification: {
                            organisation_info: it
                        }
                    };

                    //assert
                    assert.deepEqual(expectedJson, json);

                },
                "to_json will return undefined if no UUID": function () {
                    var identity = new Identity();

                    var json = identity.to_json();

                    //assert
                    assert.equal(json, undefined);

                }
            },
            "return the correct state": {
                "getState will return the state of the object": function () {
                    var identity = new Identity();

                    //given
                    getJSONReturnError = false;

                    //when
                    identity.load(crmKBData);

                    var json = identity.getState();

                    var expectedJSON = {
                        name: testORG,
                        UUID: uuid,
                        sector: it
                    };

                    //assert
                    assert.deepEqual(json, expectedJSON);

                }
            }
        }
    });
});
