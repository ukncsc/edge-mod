define([
    "dcl/dcl",
    "knockout",
    "common/cert-utils"
], function (declare, ko, Utils) {
    "use strict";
    /*
     * Refactored existing Edge Identity to use DCL to allow swapping from CRM Identity to CIQ 3.0 Identity.
     * Kept behaviour & layout similar to existing Edge Identity, marginal increase in validation.
     */

    var is_string = /^[\w\s]+$/i

    return declare(null, {
        declaredClass: "EdgeIdentity",
        constructor: function () {
            this.name = ko.observable('');
            this.roles = ko.observableArray([]);
            this.electronic_address_identifiers = ko.observableArray([]);
            this.party_name = ko.observable('');
            this.languages = ko.observableArray([]);
            this.free_text_lines = ko.observableArray([]);
            this.template = "edge-identity-element-popup";
            this.previousState = null;
        },

        load: function (data) {
            this.name(data["name"] || '');
            this.roles(data["roles"] || []);

            if (Utils.checkNestedFieldExists(data, "specification", "electronic_address_identifiers")) {
                this.electronic_address_identifiers(data["specification"]["electronic_address_identifiers"]);
            } else {
                this.electronic_address_identifiers([]);
            }

            if (Utils.checkNestedFieldExists(data, "specification", "party_name", "name_lines")) {
                this.party_name(data["specification"]["party_name"]["name_lines"][0]["value"]);
            } else {
                this.party_name('');
            }

            if (Utils.checkNestedFieldExists(data, "specification", "languages")) {
                this.languages(data.specification.languages.map(function (obj) {
                    return obj.value;
                }));
            } else {
                this.languages([]);
            }

            if (Utils.checkNestedFieldExists(data, "specification", "free_text_lines")) {
                this.free_text_lines(data.specification.free_text_lines.map(function (obj) {
                    return obj.value;
                }));
            } else {
                this.free_text_lines([]);
            }
            return this;
        },

        isFull: function (array) {
            return array.indexOf("") === -1;
        },

        emailIsFull: function () {
            var valueArray = this.electronic_address_identifiers().map(function (e_address_identifier) {
                return e_address_identifier.value
            });
            return this.isFull(valueArray);
        },

        addRole: function () {
            if (this.isFull(this.roles())) {
                this.roles.unshift('');
            }
        },

        addLanguage: function () {
            if (this.isFull(this.languages())) {
                this.languages.unshift('');
            }
        },

        addText: function () {
            if (this.isFull(this.free_text_lines())) {
                this.free_text_lines.unshift('');
            }
        },

        addEAddress: function () {
            if (this.emailIsFull()) {
                this.electronic_address_identifiers.unshift({value: ''})
            }
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
            if (this.hasName()) {  //restore if editing
                this.restoreSnapshot();
                this.modal.close(this.previousState);
            } else {       //stops list ident from populating blank identities
                this.modal.close();
            }
        },

        newIdentity: function () {
            return {
                name: this.name(),
                party_name: this.party_name(),
                roles: this.roles().slice(),
                languages: this.languages().slice(),
                electronic_address_identifiers: this.electronic_address_identifiers().slice(),
                free_text_lines: this.free_text_lines().slice()
            };
        },

        hasName: function () {
            return !!(this.name() && this.name().trim().length > 0);
        },

        to_json: function () {
            if (this.hasName()) {
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
