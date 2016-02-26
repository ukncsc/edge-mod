define([
    "../dcl/dcl",
    "knockout",
    "common/cert-abstract-builder-form"
], function (declare, ko, AbstractBuilderForm) {
    "use strict";

    return declare(AbstractBuilderForm, {
        declaredClass: "ListSelects",

        constructor: declare.superCall(function (sup) {
            return function (label, options) {
                sup.call(this, [label]);
                this.saveKey = options['saveKey'];
                this.choiceListName = options['selectChoice'];
                this.choices = ko.observableArray([]);
                this.items = ko.observableArray([]).extend({
                    requiredGrouped: {
                        required: options['required'],
                        group: this.validationGroup,
                        displayMessage: "Needs at least one " + options['displayName']
                    }
                });

                this.count = ko.computed(function () {
                    return this.items().length || "";
                }, this).extend({rateLimit: 100});
            }
        }),

        toggle: function (item) {
            if (this.isSelected(item)) {
                this.items.remove(item);
            } else {
                this.items.push(item)
            }
        },

        isSelected: function (item) {
            return this.items.indexOf(item) > -1;
        },

        loadStatic: function (options) {
            this.choices(options[this.choiceListName]);
        },

        load: function (data) {
            this.items.removeAll();
            Array.prototype.push.apply(this.items(), data[this.saveKey]);
        },

        save: function () {
            var data = {};
            data[this.saveKey] = [];
            Array.prototype.push.apply(data[this.saveKey], this.items());
            return data;
        }
    });
});

