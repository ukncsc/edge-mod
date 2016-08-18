define([
    "dcl/dcl",
    "knockout",
    "common/modal/show-error-modal"
], function (declare, ko, showErrorModal) {
    "use strict";

    return declare(null, {
        declaredClass: "CatalogMatching",
        constructor: function () {
            this.label = ko.observable("Matching");
            this.id = ko.observable("");
            this.duplicates = ko.observableArray([]);
            this.hasMatches = ko.computed( function () {
               return this.duplicates().length != 0;
            }.bind(this));
        },

        loadStatic: function (optionsList) {
            this.id(optionsList.rootId);
            this.load();
        },

        load: function () {
            postJSON("/adapter/certuk_mod/review/duplicates/" + this.id(),"", function (response) {
                this.duplicates(response["duplicates"]);
            }.bind(this));
        }
    });
});
