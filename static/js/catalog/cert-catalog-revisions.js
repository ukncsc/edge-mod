define([
    "dcl/dcl",
    "knockout",
    "common/topic",
    "catalog/cert-catalog-topics"
], function (declare, ko, Topic, topics) {
    "use strict";

    return declare(null, {
        declaredClass: "CatalogRevisions",
        constructor: function () {
            this.label = ko.observable("Revisions");
            this.revisions = ko.observableArray([]);
            this.revision = ko.observable("");
        },

        loadStatic: function (optionsList) {
            this.revisions(optionsList.revisions);
            this.revision(ko.utils.arrayFirst(this.revisions(), function(rev) {
                return rev.timekey === optionsList.revision;
            }));
            this.revision.subscribe(function (data) {
                Topic.publish(topics.REVISION, data.timekey);
            }.bind(this));
        }
    });
});
