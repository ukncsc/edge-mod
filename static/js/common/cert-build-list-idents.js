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
                this.saveGroup = options['saveGroup'] || "";
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
            var saveGroup = this.saveGroup;
            if (this.saveKey in data) {
                $.each(data[this.saveKey], function (i, v) {
                    if (saveGroup) {
                        self.items.push(new CERTIdentity().load(v[saveGroup]));
                    }
                    else {
                        self.items.push(new CERTIdentity(v));
                    }
                });
            }
        },

        remove: function (a) {
            this.items.remove(a);
        },

        save: function () {
            var data = {};
            data[this.saveKey] = [];
            var saveGroup = this.saveGroup;
            ko.utils.arrayForEach(this.items(), function (item) {
                if (saveGroup) {
                    var subData = {}
                    subData[saveGroup] = item.to_json();
                    data[this.saveKey].push(subData);
                } else {
                    data[this.saveKey].push(item.to_json());
                }
            }.bind(this));

            return data;
        }
    });
});
