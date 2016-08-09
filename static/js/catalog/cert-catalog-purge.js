define([
    "dcl/dcl",
    "knockout",
    "common/modal/show-error-modal"
], function (declare, ko, showErrorModal) {
    "use strict";

    return declare(null, {
        declaredClass: "cert-catalog-purge",
        constructor: function () {
            this.label = ko.observable("Purge");
            this.canRevoke = ko.observable("");
            this.canPurge = ko.observable("");

        },

        loadStatic: function (optionsList) {
            this.canRevoke(optionsList.canRevoke);
            this.canPurge(optionsList.canPurge);
        },

        revokeObject: function () {
           /* postJSON("/adapter/certuk_mod/review/duplicates/" + this.id(),"", function (response) {
                this.duplicates(response["duplicates"]);
            }.bind(this), function (error) {
                showErrorModal(error, false)
            }.bind(this));     */
        },

        purgeObject: function () {

        }
    });
});
