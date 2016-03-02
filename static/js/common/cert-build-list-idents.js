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
                        {requiredGrouped:
                            {required :options['required'], group: this.validationGroup, displayMessage: "Needs at least one " + options['displayName']}
                        });
                this.count = ko.computed(function () {
                    return this.items().length || "";
                }, this);
            }
        }),


        add: function () {
            var newIdent = new CERTIdentity();
            newIdent.ModelUI().done(function (context, result) {
                this.items.unshift(newIdent);
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
                    self.items.push(new CERTIdentity().load(v['identity']));
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

    return ListIdents;
});
