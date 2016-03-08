define([
    "dcl/dcl",
    "knockout"
], function (declare, ko) {
    "use strict";

    return declare(null, {
        declaredClass: "ActivityLogModel",
        constructor: function () {
            this.search = ko.observable("");

            this.loading = ko.observable(false);
            this.logContent = ko.observable(null);
            this.logError = ko.observable(null);

            this.loading.subscribe(function(isLoading) {
                document.getElementById("_loading_").style.display = isLoading ? null : "none";
            });
        },
        loadLog: function () {
            this.loading(true);
            var url = "/adapter/certuk_mod/ajax/activity_log/" + encodeURIComponent(this.search());
            getJSON(url, null, this._onLoadLogSuccess.bind(this), this._onLoadLogError.bind(this));
        },
        clearSearch: function () {
            if (!(this.search.peek() === "")) {
                this.search("");
                this.loadLog();
            }
        },
        _onLoadLogSuccess: function (data) {
            this.logError(null);
            this.logContent(data.matches);
            this.loading(false);
        },
        _onLoadLogError: function (error) {
            this.logContent(null);
            this.logError(JSON.parse(error.responseText).message);
            this.loading(false);
        }
    });
});
