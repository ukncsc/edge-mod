define([
    "dcl/dcl",
    "knockout",
    "common/cert-abstract-builder-form",
], function (declare, ko, AbstractBuilderForm) {
    "use strict";

    return declare(AbstractBuilderForm, {
        declaredClass: "identity",

        constructor: function () {
            this.searchTerm = ko.observable();
            this.searchResults = ko.observableArray([]);
            this.UUID = ko.observable();
            this.sector = ko.observable();

            this.haveQuery = ko.computed(function () {
                return this.searchTerm() != null ? this.searchTerm().trim().length > 0 : false;
            }, this);

            this.search = ko.observable(false);
            this.selected = ko.observable(false);
        },

        load: function (data) {
            this.UUID(data["uuid"] || "");
            this.sector(data["sector"] || "");
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

        searchCRM: function () {
            this.search(!this.search());
            this.searchResults([]);

            var searchUrl = this.buildSearchCRMURL() + this.searchTerm();

            getJSON(searchUrl, null, this.searchResults);
        },

        selectOrganisation: function (data) {
            this.uuid(data["uuid"]);
            this.getSector(data["uuid"]);
        },

        getSector: function(id) {
            getJSON(this.buildOrgCRMURL() + id, null, function(data) {
                this.sector(data["sector"])
            })
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

        okay: function () {
            this.modal.close(this.newIdentity());
        },

        cancel: function () {
            this.restoreSnapshot(this.previousState);
            this.modal.close(this.previousState);
        },

        clone: function () {
            return {
                UUID: this.UUID(),
                sector: this.sector()
            };
        },

        to_json: function () {
            if (this.UUID()) {
             /*   return {
                    UUID: this.UUID(),
                    sector: this.sector()
                };  */
                return this.clone();
            } else {
                return undefined
            }
        }
    })
});
