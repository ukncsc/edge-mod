define([
    "../dcl/dcl",
    "knockout",
    "common/cert-abstract-builder-form"
], function (declare, ko, AbstractBuilderForm) {
    "use strict";

    Array.prototype.chunk = function (chunkSize) {
        var array = this;
        return [].concat.apply([],
            array.map(function (elem, i) {
                return i % chunkSize ? [] : [array.slice(i, i + chunkSize)];
            })
        );
    }

    var ListSelects = declare(AbstractBuilderForm, {
        declaredClass: "ListSelects",

        constructor: declare.superCall(function (sup) {
            return function (label, options) {
                sup.call(this, [label]);
                this.saveKey = options['saveKey'];
                this.selectChoiceName = options['selectChoice'];
                this.options = ko.observableArray();

                this.optionsGrouped = ko.computed(function () {
                    return this.options().chunk(8);
                }, this);

                this.items = ko.observableArray().extend(
                    {
                        rateLimit: 200,
                        required2: {
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

        loadStatic: function (optionLists) {
            this.options(optionLists[this.selectChoiceName]);
        },


        load: function (data) {
            this.items.removeAll();
            var self = this;
            if (self.saveKey in data) {
                $.each(data[self.saveKey], function (i, v) {
                    self.items.push(v);
                });
            }
        },


        save: function () {
            var data = {};
            var saveKey = this.saveKey;
            data[saveKey] = [];
            ko.utils.arrayForEach(this.items(), function (item) {
                data[saveKey].push(item);
            });

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
                        if (element.checked) {
                            array.remove(element.defaultValue);
                            array.push(element.defaultValue);
                        }
                        else {
                            array.remove(element.defaultValue);
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

