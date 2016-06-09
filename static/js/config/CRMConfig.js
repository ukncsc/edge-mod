define([
    "dcl/dcl",
    "knockout",
    "config/base-mongo-config"
], function (declare, ko, baseMongoConfig) {

    return declare(baseMongoConfig, {
        declaredClass: "CRMConfig",
        constructor: declare.superCall(function (sup) {
            return function () {
                sup.call(this);
                this.CRMURL = ko.observable();
            }
        }),

        getURL: function () {
            this.getData("get_crm_url/", "An error occurred while attempting to retrieve the CRM configuration.")
        },

        _parseResponse: function (response) {
            this.CRMURL(response["crmURL"]);
        },

        save: function () {
            if (this.isValid(this.CRMURL())) {
                this.saveData("set_crm_url/", this.CRMURL(), "The CRM settings were saved successfully.", "An error occurred while attempting to save the CRM configuration");
            } else {
                this.createErrorModal("The CRM url must be a valid url ending with /crmapi");
            }
        },

        isValid: function (url) {
            var endsWithCRM = /crmapi$/;
            return endsWithCRM.test(url)
        }
    });

});
