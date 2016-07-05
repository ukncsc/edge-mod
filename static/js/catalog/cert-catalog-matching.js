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
            this.id = ko.observable("");
            this.duplicates = ko.observableArray([]);
        },

        loadStatic: function (optionsList) {
            this.id(optionsList.rootId)
            this.load();
        },

        load: function () {
            postJSON("duplicates/"+ this.id(), this.id(), function (response) {
                this.duplicates(response);
            }.bind(this), function (error) {
                showErrorModal(error, false)
            }.bind(this));
        }
    });
});
