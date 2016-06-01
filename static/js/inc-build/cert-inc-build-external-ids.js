define([
    "dcl/dcl",
    "knockout",
    "common/cert-abstract-builder-form",
    "inc-build/cert-inc-build-external-id"
], function (declare, ko, AbstractBuilderForm, ExternalId) {
    "use strict";

    return declare(AbstractBuilderForm, {
        declaredClass: "ExternalIds",

        constructor: declare.superCall(function (sup) {
            return function () {
                this.items = ko.observableArray([]);
                sup.call(this, "External IDs");
            }
        }),

        add: function () {
            var new_id = new ExternalId();
            this.addExternalIdValidation(new_id);
            this.items.unshift(new_id);
        },
        remove: function (a) {
            this.validationGroup.remove(a.source);
            this.validationGroup.remove(a.id);
            this.items.remove(a);
        },
        addExternalIdValidation: function (ext_id) {
            ext_id.source.extend({
                requiredGrouped: {
                    required: true,
                    group: this.validationGroup,
                    displayMessage: "You need to enter a source for your External ID"
                }
            });
            ext_id.id.extend({
                requiredGrouped: {
                    required: true,
                    group: this.validationGroup,
                    displayMessage: "You need to enter an id for your External ID"
                }
            });
        },
        load: function (data) {
            this.items.removeAll();
            var self = this;
            var saveGroup = this.saveGroup;
            if ('external_ids' in data) {
                $.each(data['external_ids'], function (i, v) {
                    var new_id = new ExternalId();
                    self.addExternalIdValidation(new_id);

                    new_id.load(v['source'], v['id'])
                    self.items.unshift(new_id);
                });
            }
        },
        save: function () {
            var data = {};
            data['external_ids'] = [];
            var saveGroup = this.saveGroup;
            ko.utils.arrayForEach(this.items(), function (item) {
                data['external_ids'].push(item.to_json());
            }.bind(this));

            return data;
        },
        counter: function () {
            return this.items().length || "";
        },
    });
});
