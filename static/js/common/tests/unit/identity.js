define([
    "intern!object",
    "intern/chai!assert",
    "common/mock-stickytape",
    "common/identity"
], function (registerSuite, assert, mstickytape, Identity) {
    "use strict";

    var testORG = "test-org";
    var testORG2 = "test-org2";
    var uuid = "54163ff2-9431-4eb0-a4ea-5e41500d30d4";
    var it = "IT";

    var crmURL = "http://10.1.1.65:8080/crmapi"

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
                },
                "select an organisation": {
                    "populate the identity": function () {
                        var identity = new Identity();

                        var data = {
                            name: testORG,
                            uuid: uuid
                        };

                        //when
                        identity.selectOrganisation(data);

                        //assert
                        assert.equal(identity.name(), testORG);
                        assert.equal(identity.UUID(), uuid);
                        assert.equal(identity.selected(), true);
                        assert.equal(identity.search(), false);
                        assert.equal(identity.sector(), "");
                    }
                },
                "can manipulate snapshots": {
                    "creates snapshot": function () {
                        var identity = new Identity();

                        identity.name(testORG);
                        identity.UUID(uuid);
                        identity.sector(it);

                        identity.createSnapshot()

                        var expectedState = {
                            name: testORG,
                            UUID: uuid,
                            sector: it
                        };

                        assert.deepEqual(identity.previousState, expectedState);
                    },
                    "restore a snapshot": function () {
                        var identity = new Identity();

                        identity.name(testORG);
                        identity.UUID(uuid);
                        identity.sector(it);

                        identity.createSnapshot()

                        identity.name("new name");
                        identity.UUID("new uuid");
                        identity.sector("new sector");

                        identity.restoreSnapshot();

                        assert.equal(identity.name(), testORG);
                        assert.equal(identity.UUID(), uuid);
                        assert.equal(identity.sector(), it);
                    }
                },
                "validate CRM UUID": {
                    "validates correct uuid": function () {
                        var identity = new Identity();

                        var validUUID = "38b9555c-ca2f-44c7-8789-bb281c60ee9f";

                        assert.isTrue(identity.isCRMUUID(validUUID));
                    },
                    "wont validate incorrect uuid": function () {
                        var identity = new Identity();

                        var invalidUUID = "38b9555cgarbage";

                        assert.isFalse(identity.isCRMUUID(invalidUUID));
                    }
                },
                "gets name": {
                    "sets name to uuid if not a crm id": function () {
                        var identity = new Identity();

                        var invalidUUID = "38b9555cgarbage";

                        identity.getName(invalidUUID)

                        assert.equal(identity.name(), invalidUUID);
                    },
                    "gets name from crm if uuid": function () {
                        var identity = new Identity();

                        //given
                        getJSONReturnError = false;

                        identity.getName("38b9555c-ca2f-44c7-8789-bb281c60ee9f");

                        assert.equal(identity.name(), "test-org");
                    }
                },
                "builds correct urls": {
                    "builds crm org url ": function () {
                        var identity = new Identity();

                        identity.CRMURL = crmURL;

                        assert.equal(identity.buildOrgCRMURL(), crmURL + "/organisations/");
                    },
                    "builds crm search url ": function () {
                        var identity = new Identity();

                        identity.CRMURL = crmURL;

                        assert.equal(identity.buildSearchCRMURL(), crmURL + "/organisations/find?organisation=");
                    }
                }
            }
        }
    );
});
