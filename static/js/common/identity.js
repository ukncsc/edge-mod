define([
    "dcl/dcl",
    "knockout",
    "common/cert-abstract-builder-form",
], function (declare, ko, AbstractBuilderForm) {
    "use strict";

    return declare(AbstractBuilderForm, {
        declaredClass: "Identity",

        constructor: function () {
            this.searchTerm = ko.observable();
            this.searchResults = ko.observableArray([]);

            this.name = ko.observable(null);
            this.UUID = ko.observable(null);
            this.sector = ko.observable(null);

            this.haveQuery = ko.computed(function () {
                return this.searchTerm() != null ? this.searchTerm().trim().length > 0 : false;
            }, this);
            this.search = ko.observable(false);
            this.selected = ko.observable(false);
        },

        buildCRMURL: function () {
            return "http://10.1.10.65:8080/crmapi";
        },

        buildOrgCRMURL: function () {
            return this.buildCRMURL() + "/organisations/"
        },

        buildSearchCRMURL: function () {
            return this.buildOrgCRMURL() + "find?organisation=";
        },

        load: function (data) {
            this.UUID(data["uuid"] || "");
            this.name(this.getName(this.UUID()));
            this.sector(data["sector"] || "");
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
            for (var key in this.previousState) {
                if (this.previousState.hasOwnProperty(key)) {
                    this[key](this.previousState[key])
                }
            }
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
                return this.clone();
            } else {
                return undefined
            }
        }
    })
});
