define([
    "dcl/dcl",
    "knockout"
], function (declare, ko) {
    "use strict";

    return declare(null, {
        declaredClass: "ActivityLogModel",
        constructor: function () {
            this.filterUser = ko.observable("");
            this.filterCategory = ko.observable("");
            this.filterState = ko.observable("");
            this.filterMessage = ko.observable("");

            this.loading = ko.observable(false);
            this.logContent = ko.observable(null);
            this.logError = ko.observable(null);

            this.validCategories = ko.observableArray(["AGEING", "DEDUP"]);
            this.validStates = ko.observableArray(["FATAL", "ERROR", "WARN", "INFO", "DEBUG", "TRACE"]);
        },
        loadLog: function () {
            this.loading(true);
            var url = [
                "/adapter/certuk_mod/ajax/activity_log/",
                this.filterUser() || "*",
                "/",
                this.filterCategory() || "*",
                "/",
                this.filterState() || "*",
                "/",
                this.filterMessage() || "*",
                "/50"
            ].join("");
            getJSON(url, null, this._onLoadLogSuccess.bind(this), this._onLoadLogError.bind(this));
        },
        _onLoadLogSuccess: function (data) {
            this.logContent(data.matches);
            this.loading(false);
        },
        _onLoadLogError: function (error) {
            this.logError(error);
            this.loading(false);
        }
    });
});
