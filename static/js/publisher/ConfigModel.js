define([
    "dcl/dcl",
    "knockout",
    "common/modal/Modal",
    "kotemplate!config-modal:./templates/config-modal-content.html"
], function (declare, ko, Modal, publishModalTemplate) {
    "use strict";

    function constructSite (siteInfo) {
        return {
            site_id: siteInfo["site_id"] || "",
            name: siteInfo["name"],
            is_publish_site: ko.observable(!!siteInfo["is_publish_site"])
        };
    }

    return declare(null, {
        constructor: function () {
            this.sites = ko.observableArray([]);
            this.selectedSite = ko.observable(null);
            this.publishId = ko.observable(null);
            this.gotSites = ko.observable(false);
        },

        getSites: function () {
            postJSON("../ajax/get_sites/", { }, this._onSitesRetrieved.bind(this));
        },

        _onSitesRetrieved: function (response) {
            if (response["success"]) {
                var newSites = [];
                this.selectedSite(null);
                this.publishId(null);
                ko.utils.arrayForEach(response["sites"], function (item) {
                    var site = constructSite(item);
                    if (site.is_publish_site()) {
                        this.selectedSite(site);
                        this.publishId(site.site_id);
                    }
                    newSites.push(site);
                }.bind(this));
                this.sites(newSites);
                this.gotSites(true);
            } else {
                var errorModal = new Modal({
                    title: "Error",
                    titleIcon: "glyphicon-exclamation-sign",
                    contentData: "An error occurred while attempting to retrieve the list of possible sites."
                });
                errorModal.show();
            }
        },

        _modalOnSaveSite: function (modal) {
            var yesButton = modal.getButtonByLabel("Yes");
            var noButton = modal.getButtonByLabel("No");
            var closeButton = modal.getButtonByLabel("Close");

            yesButton.hide(true);
            noButton.hide(true);
            closeButton.hide(false);
            closeButton.disabled(true);

            modal.contentData.waitingForResponse(true);
            modal.contentData.message("Saving...");

            this.savePublishSite(function (response) {
                modal.contentData.waitingForResponse(false);

                var success = !!(response["success"]);
                var errorMessage = response["error_message"];
                if (errorMessage) {
                    errorMessage = errorMessage.replace(/^[A-Z]/, function (match) {
                        return match.toLowerCase();
                    }).replace(/[,.]+$/, "");
                }
                var message = success?
                    "The publisher site was saved." :
                    "An error occurred while attempting to save (" + errorMessage + "). Would you like to try again?";
                var title = success ? "Success" : "Error";
                var titleIcon = success ? "glyphicon-ok-sign" : "glyphicon-exclamation-sign";

                yesButton.hide(success);
                noButton.hide(success);
                closeButton.hide(!success);
                closeButton.disabled(!success);

                modal.contentData.message(message);
                modal.title(title);
                modal.titleIcon(titleIcon);

                if (success) {
                    var publishId = response["saved_id"];
                    this.publishId(publishId);
                    ko.utils.arrayForEach(this.sites(), function (site) {
                        var isPublish = publishId === site.site_id;
                        site.is_publish_site(isPublish);
                    });
                }

            }.bind(this));
        },

        _onShowSaveModal: function (modal) {
            var siteSelected = !!(this.selectedSite());

            if (siteSelected) {
                // Save!
                this._modalOnSaveSite.call(this, modal);
            } else {
                // Warn before save
                modal.contentData.message("Selecting 'None' will remove the publish site. Are you sure?");

                var yesButton = modal.getButtonByLabel("Yes");
                var noButton = modal.getButtonByLabel("No");
                var closeButton = modal.getButtonByLabel("Close");

                yesButton.hide(false);
                noButton.hide(false);
                closeButton.hide(true);
            }
        },

        onSavePublishSite: function () {
            var contentData = {
                message: ko.observable(""),
                waitingForResponse: ko.observable(false)
            };

            var onSaveModal = new Modal({
                title: "Save settings",
                titleIcon: "glyphicon-cloud-upload",
                contentData: contentData,
                contentTemplate: publishModalTemplate.id,
                onShow: this._onShowSaveModal.bind(this),
                buttonData: [
                    {
                        label: "Yes",
                        noClose: true,
                        callback: this._modalOnSaveSite.bind(this),
                        disabled: ko.observable(false),
                        icon: "glyphicon-ok",
                        hide: ko.observable(true)
                    },
                    {
                        label: "No",
                        icon: "glyphicon-remove",
                        disabled: ko.observable(false),
                        hide: ko.observable(true)
                    },
                    {
                        label: "Close",
                        hide: ko.observable(true),
                        disabled: ko.observable(true)
                    }
                ]
            });

            onSaveModal.show();
        },

        savePublishSite: function (onSavePublishSiteCallback) {
            postJSON("../ajax/set_publish_site/", {
                site_id: this.selectedSite() ? this.selectedSite().site_id : ""
            }, onSavePublishSiteCallback.bind(this));
        }
    });
});
