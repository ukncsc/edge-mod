define([
    "dcl/dcl",
    "knockout",
    "common/modal/show-error-modal"
], function (declare, ko, showErrorModal) {
    "use strict";

    return declare(null, {
        declaredClass: "Matching",
        constructor: function () {
            this.label = ko.observable("Matching");
            this.ajax_uri = ko.observable("");
            this.duplicates = ko.observableArray([]);
        },

        loadStatic: function (optionsList) {
            this.ajax_uri(optionsList.ajax_uri)
        },

        load: function () {
            postJSON(this.ajax_uri() + 'get_activity/', params, function (response) {
                this.duplicates(response);
            }.bind(this), function (error) {
                showErrorModal(error, false)
            }.bind(this));
        }
    });
});
