define([
    "dcl/dcl",
    "knockout",
    "common/cert-abstract-builder-form",
    "text!config-service"
], function (declare, ko, AbstractBuilderForm, configText) {
    "use strict";

    var config = Object.freeze(JSON.parse(configText));

    var Identity = declare(AbstractBuilderForm, {
        declaredClass: "Identity",

        constructor: function () {
            this.CRMURL = config.crmURL;
            this.searchTerm = ko.observable(null);
            this.searchResults = ko.observableArray([]);

            this.name = ko.observable(null);
            this.UUID = ko.observable(null);
            this.sector = ko.observable(null);

            this.haveQuery = ko.computed(function () {
                return typeof this.searchTerm() === "string" && this.searchTerm().trim().length > 0;
            }, this);
            this.search = ko.observable(false);
            this.selected = ko.observable(false);
            this.error = ko.observable(false);
        },

        buildOrgCRMURL: function () {
            return this.CRMURL + "/organisations/";
        },

        buildSearchCRMURL: function () {
            return this.buildOrgCRMURL() + "find?organisation=";
        },

        load: function (data) {
            this.UUID(data["name"] || "");
            this.getName(this.UUID());
            this.sector(data["specification"]["organisation_info"] || "");
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
            getJSON(this.buildOrgCRMURL() + id, null, function (data) {
                this.name(data["name"]);
            }.bind(this), function () {
                this.name(id)
            }.bind(this));
        },

        searchCRM: function () {
            this.search(true);
            this.searchResults([]);

            var searchUrl = this.buildSearchCRMURL() + this.searchTerm();

            getJSON(searchUrl, null, function (data) {
                this.searchResults(data);
            }.bind(this), function () {
                this.error(true);
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
            getJSON(this.buildOrgCRMURL() + id, null, function (data) {
                this.sector(data["industry"] || "");
            }.bind(this));
        },

        createSnapshot: function () {
            this.previousState = this.getState();
        },

        restoreSnapshot: function () {
            ko.utils.objectForEach(this.previousState, function (key, value){
                this[key](value);
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
            this.restoreSnapshot();
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
                        organisation_info: this.sector()
                    }
                }
            } else {
                return undefined
            }
        }
    });

    return Identity;
});
