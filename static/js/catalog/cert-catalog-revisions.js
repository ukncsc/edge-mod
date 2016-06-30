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
        },

        loadStatic: function (optionsList) {
            this.revisions(optionsList.revisions);
        },

        load: function (data) {
            this.revision(data["revision"]);
            this.revision.subscribe(function (data) {
                Topic.publish(topics.REVISION, data);
            }.bind(this));
        }
    });
});
