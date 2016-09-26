define([
    "dcl/dcl",
    "knockout",
    "config/base-mongo-config"
], function (declare, ko, baseMongoConfig) {

    return declare(baseMongoConfig, {
        declaredClass: "CRMConfig",
        constructor: declare.superCall(function (sup) {
            return function () {
                sup.call(this, "get_crm_config/", "An error occurred while attempting to retrieve the CRM configuration.");
                this.CRMURL = ko.observable("");
                this.savedCRMURL = ko.observable("");

                this.enabled.subscribe(this._onEnabledChanged.bind(this));
                this.changesPending = ko.computed(this.changesPending, this);
            }
        }),

        _parseResponse: function (response) {
            if (response != null) {
                this.CRMURL(response["value"]["crm_url"] || "");
                this.savedCRMURL(response["value"]["crm_url"] || "");
                this.enabled(response["value"]["enabled"] || false);
                this.savedEnabled(response["value"]["enabled"] || false);
            }
        },

        save: function () {
            if (this.isValid(this.CRMURL())) {
                this.saveData("set_crm_config/", this.createCRMConfig(), "The CRM settings were saved successfully.", "An error occurred while attempting to save the CRM configuration");
            } else {
                this.createErrorModal("The CRM url must be a valid url ending with /crmapi");
            }
        },

        _onSuccesfulSave: function (response, successMessage) {
                    var modal = this.createSuccessModal(successMessage);

                    this.savedCRMURL(this.CRMURL());
                    this.savedEnabled(this.enabled());

                    modal.show();
        },

        changesPending: function () {
            return this.gotConfig() &&
                (
                    this.CRMURL() != this.savedCRMURL() ||
                    this.enabled() != this.savedEnabled()
                );
        },

        _onEnabledChanged: function () {
            if (!(this.enabled())) {
                this.CRMURL(this.savedCRMURL());
            }
        },

        isValid: function (url) {
            if (this.enabled()) {
                var endsWithCRM = /crmapi$/;
                return endsWithCRM.test(url)
            } else {
                return true
            }
        },

        createCRMConfig: function () {
            return {
                "value": {
                    "crm_url": this.CRMURL(),
                    "enabled": this.enabled()
                }
            }
        }
    });

});
