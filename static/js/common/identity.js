define([
    "dcl/dcl",
    "knockout",
    "common/cert-abstract-builder-form"
], function (declare, ko, AbstractBuilderForm) {
    "use strict";

    return declare(AbstractBuilderForm, {
        declaredClass: "Identity",

        constructor: function () {
            this.CRMURL = "http://10.1.10.65:8080/crmapi"        //getCRMURL
            this.searchTerm = ko.observable(null);
            this.searchResults = ko.observableArray([]);

            this.name = ko.observable(null);
            this.UUID = ko.observable(null);
            this.sector = ko.observable(null);

            this.haveQuery = ko.computed(function () {
                return typeof this.searchTerm() === "string" ? this.searchTerm().trim().length > 0 : false;
            }, this);
            this.search = ko.observable(false);
            this.selected = ko.observable(false);
        },

        buildOrgCRMURL: function () {
            return this.CRMURL + "/organisations/";
        },

        buildSearchCRMURL: function () {
            return this.buildOrgCRMURL() + "find?organisation=";
        },

        load: function (data) {
            this.UUID(data["name"] || "");
            this.name(this.getName(this.UUID()));
            this.sector(this.getSector(this.UUID()));
            this.selected(true);
            return this;
        },

        getName: function (id) {
            getJSON(this.buildOrgCRMURL() + id, null, function (data) {
                this.name(data["name"] || "");
            }.bind(this));
        },

        searchCRM: function () {
            this.search(true);
            this.searchResults([]);

            var searchUrl = this.buildSearchCRMURL() + this.searchTerm();

            getJSON(searchUrl, null, this.searchResults);
        },

        selectOrganisation: function (data) {
            this.name(data["name"]);
            this.UUID(data["uuid"]);
            this.getSector(data["uuid"]);

            this.selected(true);
            this.search(false);
        },

        getSector: function (id) {
            getJSON(this.buildOrgCRMURL() + id, null, function (data) {
                this.sector(data["industry"] || "");
            }.bind(this));
        },

        createSnapshot: function () {
            this.previousState = this.clone();
        },

        restoreSnapshot: function () {
            ko.utils.objectForEach(this.previousState, function (key, value) {
                this[key] = value;
            }.bind(this));
        },

        onSelect: function (data) {
            this.selectOrganisation(data);
            this.searchTerm("");
            this.okay();
        },

        okay: function () {
            this.modal.close(this.clone());
        },

        cancel: function () {
            this.restoreSnapshot(this.previousState);
            this.modal.close(this.previousState);
        },

        clone: function () {
            return {
                name: this.name(),
                UUID: this.UUID(),
                sector: this.sector()
            };
        },

        to_json: function () {
            if (this.UUID()) {
                return {
                    name: this.UUID()
                }
            } else {
                return undefined
            }
        }
    })
});
