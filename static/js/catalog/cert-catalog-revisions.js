define([
    "dcl/dcl",
    "knockout",
    "common/topic",
    "catalog/cert-catalog-topics"
], function (declare, ko, Topic, topics) {
    "use strict";

    return declare(null, {
        declaredClass: "Revisions",
        constructor: function () {
            this.label = ko.observable("Revisions");
            this.revisions = ko.observableArray([]);
            this.revision = ko.observable();
            this.revision.subscribe(function (data) {
                Topic.publish(topics.REVISION, data.timekey);
            }.bind(this));
        },

        loadStatic: function (optionsList) {
            this.revisions(optionsList.revisions);
        }
    });
});
