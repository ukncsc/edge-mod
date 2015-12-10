define([
    "dcl/dcl",
    "knockout",
    "common/modal/Modal",
    "kotemplate!ret-config-modal:./templates/config-modal-content.html"
], function (declare, ko, Modal, configModalTempalte) {
    "use strict";

    function inputIsInteger (value) {
        return /*typeof value === "number" &&*/ isFinite(value) && Math.floor(value) /*=*/== value;
    }

    return declare(null, {
        declaredClass: "RetentionConfig",
        constructor: function () {
            this.age = ko.observable();
            this.sightings = ko.observable();
            this.backLinks = ko.observable();

            this.savedAge = ko.observable();
            this.savedSightings = ko.observable();
            this.savedBackLinks = ko.observable();

            this.gotConfig = ko.observable(false);

            this.canSave = ko.computed(this._canSave, this);
        },

        getConfig: function () {
            this.gotConfig(false);
            postJSON("../ajax/get_retention_config/", { }, function (response) {
                this.gotConfig(true);
                if (response["success"]) {
                    this.age(response["max_age_in_months"]);
                    this.savedAge(response["max_age_in_months"]);

                    this.sightings(response["minimum_sightings"]);
                    this.savedSightings(response["minimum_sightings"]);

                    this.backLinks(response["minimum_back_links"]);
                    this.savedBackLinks(response["minimum_back_links"]);
                } else {
                    var errorModal = new Modal({
                    title: "Error",
                        titleIcon: "glyphicon-exclamation-sign",
                        contentData: "An error occurred while attempting to retrieve the retention configuration."
                    });
                    errorModal.show();
                }
            }.bind(this));
        },

        _canSave: function () {
            return this.gotConfig() &&
                (
                    this.age() != this.savedAge() ||
                    this.sightings() != this.savedSightings() ||
                    this.backLinks() != this.savedBackLinks()
                );
        },

        _save: function (modal) {
            var errors = [];

            if (!inputIsInteger(this.age())) {
                errors.push("The maximum age must be an integer.");
            } else if (this.age() < 1) {
                errors.push("The maximum age must be greater than zero.");
            }

            if (!inputIsInteger(this.sightings())) {
                errors.push("The minimum sightings must be an integer.");
            } else if (this.sightings() < 2) {
                errors.push("The minimum sightings must be greater than one.");
            }

            if (!inputIsInteger(this.backLinks())) {
                errors.push("The minimum back links must be an integer.");
            } else if (this.backLinks() < 1) {
                errors.push("The minimum back links must be greater than zero.");
            }

            var modalContent = modal.contentData;
            if (errors.length > 0) {
                modalContent.waitingForResponse(false);
                modalContent.message(errors.join(" "));
                modal.title("Error");
                modal.titleIcon("glyphicon-exclamation-sign");
            } else {
                modalContent.waitingForResponse(true);
                modalContent.message("Saving...");
                modal.getButtonByLabel("Close").disabled(true);

                postJSON("../ajax/set_retention_config/", {
                    max_age_in_months: Number(this.age()),
                    minimum_sightings: Number(this.sightings()),
                    minimum_back_links: Number(this.backLinks())
                }, function (response) {
                    modalContent.waitingForResponse(false);
                    modal.getButtonByLabel("Close").disabled(false);

                    var success = !!(response["success"]);

                    var title = success ? "Success" : "Error";
                    var titleIcon = success ? "glyphicon-ok-sign" : "glyphicon-exclamation-sign";
                    var message = success ? "The retention settings were saved successfully." :
                        "An error occurred while attempting to save (" + response["error_message"] + ").";

                    modalContent.message(message);
                    modal.title(title);
                    modal.titleIcon(titleIcon);

                    if (success) {
                        this.savedAge(this.age());
                        this.savedSightings(this.sightings());
                        this.savedBackLinks(this.backLinks());
                    }
                }.bind(this));
            }
        },

        onSave: function () {
            var contentData = {
                message: ko.observable(""),
                waitingForResponse: ko.observable(false)
            };

            var onSaveModal = new Modal({
                title: "Save settings",
                titleIcon: "glyphicon-cloud-upload",
                contentData: contentData,
                contentTemplate: configModalTempalte.id,
                onShow: this._save.bind(this),
                buttonData: [
                    {
                        label: "Close",
                        hide: ko.observable(false),
                        disabled: ko.observable(false)
                    }
                ]
            });

            onSaveModal.show();
        }
    });
});
