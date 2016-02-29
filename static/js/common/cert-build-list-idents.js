define([
    "../dcl/dcl",
    "knockout",
    "common/cert-abstract-builder-form",
    "common/cert-identity",
    "common/jquery-shim"
], function (declare, ko, AbstractBuilderForm, CERTIdentity, $) {
    "use strict";

    return declare(AbstractBuilderForm, {
        declaredClass: "ListIdents",

        constructor: declare.superCall(function (sup) {
            return function (label, options) {
                this.items = ko.observableArray([]);
                sup.call(this, [label]);
                this.saveKey = options['saveKey'];
                this.items.extend({
                    requiredGrouped: {
                        required: options['required'],
                        group: this.validationGroup,
                        displayMessage: "Needs at least one " + options['displayName']
                    }
                });

            }
        }),

        counter: function () {
            return this.items().length || "";
        },

        add: function () {
            var newIdentity = new CERTIdentity();
            newIdentity.ModelUI().done(function () {
                this.items.unshift(newIdentity);
            }.bind(this));
        },

        showUi: function (model, ident) {
            ident.ModelUI();
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
            data[this.saveKey] = [];
            ko.utils.arrayForEach(this.items(), function (item) {
                data[this.saveKey].push({'identity': item.to_json()});
            }.bind(this));

            return data;
        }
    });
});
