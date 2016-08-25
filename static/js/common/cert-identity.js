define([
    "dcl/dcl",
    "knockout",
    "common/cert-abstract-builder-form",
    "common/cert-utils"
], function (declare, ko, AbstractBuilderForm, Utils) {
    "use strict";

    var CERTIdentity = declare(AbstractBuilderForm, {
        declaredClass: "CERTIdentity",

        constructor: function () {
            this.searchTerm = ko.observable(null);
            this.searchResults = ko.observableArray([]);

            this.name = ko.observable(null);
            this.UUID = ko.observable(null);
            this.sector = ko.observable("");
            this.haveQuery = ko.computed(function () {
                return typeof this.searchTerm() === "string" && this.searchTerm().trim().length > 0;
            }, this);
            this.search = ko.observable(false);
            this.selected = ko.observable(false);
            this.error = ko.observable(false);
        },

        load: function (data) {
            this.UUID(data["name"] || "");
            this.getName(this.UUID());
            if (Utils.checkNestedFieldExists(data, "specification", "organisation_info", "industry_type")) {
                this.sector(data["specification"]["organisation_info"]["industry_type"] || "");
            }
            this.selected(true);
            return this;
        },

        getName: function (id) {
            if (this.isCRMUUID(id)) {
                this.getNameFromCRM(id);
            } else {
                this.name(id);
            }
        },

        isCRMUUID: function (value) {
            var isUUID = /^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i;
            return isUUID.test(value)
        },

        getNameFromCRM: function (id) {
            postJSON("/adapter/certuk_mod/crm/organisation/", id, function (data) {
                if (data["success"] === true) {
                    this.name(data["results"]["name"]);
                } else {
                    this.name(id);
                }
            }.bind(this));
        },

        searchCRM: function () {
            this.search(true);
            this.searchResults([]);

            postJSON("/adapter/certuk_mod/crm/find/", this.searchTerm(), function (data) {
                if (data["success"] === true) {
                    this.searchResults(data["results"]);
                } else {
                    this.error(true);
                }
            }.bind(this));
        },

        selectOrganisation: function (data) {
            this.name(data["name"]);
            this.UUID(data["uuid"]);
            this.getSector(data["uuid"]);

            this.selected(true);
            this.search(false);
        },

        getSector: function (id) {
            postJSON("/adapter/certuk_mod/crm/organisation/", id, function (data) {
                if (Utils.checkNestedFieldExists(data, "results", "industry")) {
                    this.sector(data["results"]["industry"] || "");
                }
            }.bind(this));
        },

        onSelect: function (data) {
            this.selectOrganisation(data);
            this.searchTerm("");
            this.okay();
        },

        okay: function () {
            this.modal.close(this.getState());
        },

        cancel: function () {
            this.search(false);
            this.searchTerm(null);
            this.modal.close();
        },

        getState: function () {
            return {
                name: this.name(),
                UUID: this.UUID(),
                sector: this.sector()
            }
        },

        to_json: function () {
            if (this.UUID()) {
                return {
                    name: this.UUID(),
                    specification: {
                        organisation_info: {
                            industry_type: this.sector()
                        }
                    }
                }
            } else {
                return undefined
            }
        }
    });

    return CERTIdentity;
});
