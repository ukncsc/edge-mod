define(["knockout", "dcl/dcl"], function (ko, declare) {
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
        },

        getSites: function () {
            // TODO: make base url a parameter (perhaps pass in during Django template rendering stage)
            postJSON("/adapter/publisher/ajax/get_sites/", { }, this._onSitesRetrieved.bind(this));
        },

        _onSitesRetrieved: function (response) {
            if (response["success"]) {
                var context = this;
                var newSites = [];
                context.selectedSite(null);
                context.publishId(null);
                ko.utils.arrayForEach(response["sites"], function (item) {
                    var site = constructSite(item);
                    if (site.is_publish_site()) {
                        context.selectedSite(site);
                        context.publishId(site.site_id);
                    }
                    newSites.push(site);
                });
                this.sites(newSites);
            } else {
                // TODO: Remove "view" logic, i.e. set some error flag on the model, let the view respond to it
                alert(response["error_message"]);
            }
        },

        savePublishSite: function () {
            if (!(this.selectedSite()) && !confirm("Selecting 'None' will remove the publish site. Are you sure?")) {
                return;
            }
            postJSON("/adapter/publisher/ajax/set_publish_site/", {
                site_id: this.selectedSite() ? this.selectedSite().site_id : ""
            }, this._onPublishSiteSaved.bind(this));
        },

        _onPublishSiteSaved: function (response) {
            if (response["success"]) {
                var publishId = response["saved_id"];
                this.publishId(publishId);
                ko.utils.arrayForEach(this.sites(), function (site) {
                    var isPublish = publishId === site.site_id;
                    site.is_publish_site(isPublish);
                });
                alert("Configuration saved.");
            } else {
                alert(response["error_message"]);
            }
        }
    });
});
