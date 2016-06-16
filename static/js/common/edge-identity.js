define([
    "dcl/dcl",
    "knockout"
], function (declare, ko) {
    "use strict";

    return declare(null, {
        declaredClass: "EdgeIdentity",
        constructor: function (params) {
            this.name = ko.observable('Click to edit');
            this.roles = ko.observableArray([]);
            this.electronic_address_identifiers = ko.observableArray([]);
            this.party_name = ko.observable('');
            this.languages = ko.observableArray([]);
            this.free_text_lines = ko.observableArray([]);
            this.template = "identity-element-popup";

            // from http://stix.mitre.org/language/version1.1.1/xsddocs/XMLSchema/extensions/identity/ciq_3.0/1.1.1/xPIL_xsd.html#ElectronicAddressIdentifiers_ElectronicAddressIdentifiers_ElectronicAddressIdentifier_Type
            // the XSD defines an enumeration that python-stix does not enforce.  For simplicity, we are enforcing this on the front-end directly.
            this.electronic_address_types = ko.observableArray(['AIM', 'EMAIL', 'GOOGLE', 'GIZMO', 'ICQ', 'JABBER', 'MSN', 'SIP', 'SKYPE', 'URL', 'XRI', 'YAHOO']);

            this.previousState = null;
        },

        load: function (params) {
            this.name(params["name"] || 'Click to edit');
            this.roles(params["roles"] || []);
            this.electronic_address_identifiers(params["specification"]["electronic_address_identifiers"] || []);

            if (params && params.specification && params.specification.party_name) {
                this.party_name(params["specification"]["party_name"]["name_lines"][0]["value"]);
            } else {
                this.party_name('');
            }

            if (params && params.specification && params.specification.languages) {
                this.languages(params.specification.languages.map(function (obj) {
                    return obj.value;
                }));
            } else {
                this.languages([]);
            }

            if (params && params.specification && params.specification.free_text_lines) {
                this.free_text_lines(params.specification.free_text_lines.map(function (obj) {
                    return obj.value;
                }));
            } else {
                this.free_text_lines([]);
            }
            return this;
        },

        addRole: function () {
            this.roles.unshift('');
        },

        addLanguage: function () {
            this.languages.unshift('');
        },

        addText: function () {
            this.free_text_lines.unshift('');
        },

        addEAddress: function () {
            this.electronic_address_identifiers.unshift({value: '', type: ''})
        },

        createSnapshot: function () {
            this.previousState = this.newIdentity();
        },

        restoreSnapshot: function () {
            for (var key in this.previousState) {
                if (this.previousState.hasOwnProperty(key)) {
                    this[key](this.previousState[key])
                }
            }
        },

        okay: function () {
            if (!is_string.test(this.name())) {
                $('#identity_name').parent().append(alert_danger("This field may not be empty and may only contain letters, numbers and spaces"))
                return;
            }
            this.modal.close(this.newIdentity());
        },

        cancel: function () {
            this.restoreSnapshot();
            this.modal.close(this.previousState);
        },

        newIdentity: function () {
            /*
             Note: All arrays are Spliced to 'deep' copy and prevent ko from mutating our reference
             */
            return {
                name: this.name(),
                party_name: this.party_name(),
                roles: this.roles().slice(),
                languages: this.languages().slice(),
                electronic_address_identifiers: this.electronic_address_identifiers().slice(),
                free_text_lines: this.free_text_lines().slice()
            };
        },

        to_json: function () {
            if (this.name() !== 'Click to edit')	// return empty if default name
            {
                return {
                    "name": this.name(),
                    "roles": this.roles(),
                    "specification": {
                        "party_name": {
                            "name_lines": [
                                {"value": this.party_name(), "type": "string"}
                            ]
                        },
                        "languages": this.languages().map(function (obj) {
                            return {"value": obj, "type": "string"}
                        }),
                        "free_text_lines": this.free_text_lines().map(function (obj) {
                            return {"value": obj, "type": "string"}
                        }),
                        "electronic_address_identifiers": this.electronic_address_identifiers()
                    }
                };
            } else {
                return undefined
            }
        }


    });

});
