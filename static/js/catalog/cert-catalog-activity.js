define([
    "dcl/dcl",
    "knockout",
    "common/modal/show-error-modal"
], function (declare, ko, showErrorModal) {
    "use strict";

    return declare(null, {
        declaredClass: "cert-catalog-activity",
        constructor: function () {
            this.label = ko.observable("Activity");
            this.activity_log = ko.observableArray([]);
            this.action_choices = ko.observableArray([]);
            this.action_selected = ko.observable("");
            this.action_note = ko.observable("");
        },

        load: function () {
            var params = this.generateParams();
            postJSON(ajax_uri + 'get_activity/', params, function (response) {
                this.action_choices.removeAll();
                ko.utils.arrayForEach(response['actions'], function (action) {
                    this.action_choices.push({id: action[0], descriptions: action[1]})
                });

                this.activity_log.removeAll();
                ko.utils.arrayForEach(response['entries'], function (entry) {
                    this.activity_log.push(entry);
                })
            }.bind(this), function (error) {
                showErrorModal(error, false)
            }.bind(this));
        },

        loadStatic: function (optionsList) {

        },

        generateParams: function () {
            return {
                stix_id: stix_id,
                action_id: this.action_selected().id,
                note: this.action_note()
            }
        },

        recordActivity: function () {

        }
    });
});
