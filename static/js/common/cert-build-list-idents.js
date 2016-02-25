define([
    "../dcl/dcl",
    "knockout",
    "common/cert-abstract-builder-form",
    "common/cert-identity"
], function (declare, ko, AbstractBuilderForm, CERTIdentity) {
    "use strict";

    var ListIdents = declare(AbstractBuilderForm, {
        declaredClass: "ListIdents",

        constructor: declare.superCall(function (sup) {
            return function (label, options) {
                sup.call(this, [label]);
                this.saveKey = options['saveKey'];

                this.items = ko.observableArray([]).extend(
                        {required2:
                            {required :options['required'], group: this.validationGroup, displayMessage: "Needs at least one " + options['displayName']}
                        });
                this.count = ko.computed(function () {
                    return this.items().length || "";
                }, this);
            }
        }),


        add: function () {
            var newItem = new CERTIdentity();
            var items = this.items;
            newItem.ModelUI().done(function (context, result) {
                items.unshift(newItem);
            });
        },

        show_ui: function (model, data) {
            data.ModelUI();
        },

        load: function (data) {
            this.items.removeAll();
            var self = this;
            if (this.saveKey in data) {
                $.each(data[this.saveKey], function (i, v) {
                    self.items.push(new CERTIdentity(v['identity']));
                });
            }
        },

        remove: function (a) {
            this.items.remove(a);
        },

        save: function () {
            var data = {};
            var saveKey = this.saveKey;
            data[saveKey] = [];
            ko.utils.arrayForEach(this.items(), function (item) {
                data[saveKey].push({'identity': item.to_json()});
            });

            return data;
        }
    });

    return ListIdents;
});
