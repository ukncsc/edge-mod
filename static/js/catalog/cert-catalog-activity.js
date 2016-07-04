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
            this.stix_id = ko.observable("");
            this.ajax_uri = ko.observable("");
        },

        load: function (params) {
            postJSON(this.ajax_uri() + 'get_activity/', params, function (response) {
                this.action_choices.removeAll();
                ko.utils.arrayForEach(response['actions'], function (action) {
                    this.action_choices.push({id: action[0], description: action[1]})
                }.bind(this));

                this.activity_log.removeAll();
                ko.utils.arrayForEach(response['entries'], function (entry) {
                    this.activity_log.push(entry);
                }.bind(this))
            }.bind(this), function (error) {
                showErrorModal(error, false)
            }.bind(this));
        },

        loadStatic: function (optionsList) {
            this.stix_id(optionsList["rootId"]);
            this.ajax_uri(optionsList["ajax_uri"]);

            var params = {
                "id": this.stix_id(),
                "revision": "latest"
            }
            this.load(params);
        },

        recordActivity: function () {
            var params = {
                stix_id: this.stix_id(),
                action_id: this.action_selected().id,
                note: this.action_note()
            };
            postJSON(ajax_uri + 'add_activity/', params, function (response) {
                this.action_note('');
                this.activity_log.push(response['entry']);
            }.bind(this), function (error) {
                showErrorModal(error, false)
            }.bind(this));
        }
    });
});
