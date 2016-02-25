define([
    "../dcl/dcl",
    "knockout",
    "common/cert-abstract-builder-form"
], function (declare, ko, AbstractBuilderForm) {
    "use strict";

    var ListSelects = declare(AbstractBuilderForm, {
        declaredClass: "ListSelects",

        constructor: declare.superCall(function (sup) {
            return function (label, options) {
                sup.call(this, [label]);
                this.saveKey = options['saveKey'];
                this.choiceListName = options['selectChoice'];
                this.choices = ko.observableArray([]);
                this.items = ko.observableArray().extend(
                    {
                        rateLimit: 200,
                        requiredGrouped: {
                            required: options['required'],
                            group: this.validationGroup,
                            displayMessage: "Needs at least one " + options['displayName']
                        }
                    });

                this.count = ko.computed(function () {
                    return this.items().length || "";
                }, this);
            }
        }),

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

    ko.bindingHandlers.bsChecked = {
        init: function (element, valueAccessor, allBindingsAccessor,
                        viewModel, bindingContext) {

            var id = valueAccessor().id;
            var array = valueAccessor().array;

            ko.utils.arrayForEach(array(), function (item) {
                if (item === id) {
                    element.setAttribute('checked', true);
                    element.parentNode.className = element.parentNode.className + " active";
                }
            });


            var newValueAccessor = function () {
                return {
                    change: function () {
                        array.remove(element.defaultValue);
                        if (element.checked) {
                            array.push(element.defaultValue);
                        }
                    }
                }
            };


            ko.bindingHandlers.event.init(element, newValueAccessor,
                allBindingsAccessor, viewModel, bindingContext);
        },
    }

    return ListSelects;
});

