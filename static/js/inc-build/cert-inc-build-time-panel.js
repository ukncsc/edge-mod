define([
    "dcl/dcl",
    "knockout",
    "common/cert-abstract-builder-form",
    "inc-build/cert-inc-build-time"
], function (declare, ko, AbstractBuilderForm, Time) {
    "use strict";


    return declare(AbstractBuilderForm, {
        declaredClass: "Times",

        constructor: declare.superCall(function (sup) {
            return function () {
                sup.call(this, "Times");
                //this.time_zones_list = ko.observableArray([]);
                this.time_types = ko.observableArray();

                this.count = ko.computed(function () {
                    var count = 0;
                    ko.utils.arrayForEach(this.time_types(), function (time_type) {
                        if (time_type.time_string() != "") {
                            count++;
                        }
                    });
                    return count != 0 ? count : "";
                }, this).extend({rateLimit: 300});

            }
        }),

        loadStatic: function (optionsList) {
            $('.btn').button();
            this.time_types.removeAll();
            for (var i = 0; i < optionsList['time_types_list'].length; i++) {
                this.time_types.push(new Time(optionsList['time_types_list'][i][0], optionsList['time_types_list'][i][1]));
            }
        },

        load: function (data) {
            var self = this;
            ko.utils.arrayForEach(self.time_types(), function (time_type) {
                time_type.load("");
            });


            if ('time' in data) {
                $.each(data['time'], function (i, v) {
                    ko.utils.arrayForEach(self.time_types(), function (time_type) {
                        if (time_type.save_name() === i) {
                            time_type.load(v);
                        }
                    });
                });
            }
        },

        ButtonsExampleViewModel: function () {
            this.isToggled = ko.observable(false);
        },


        save: function () {
            var data = {};
            var self = this;
            var data_time = {};

            ko.utils.arrayForEach(this.time_types(), function (item) {
                var time = {};
                if (item.time_string() != "") {
                    data_time[item.save_name()] = {
                        'value': item.time_string(),
                        'precision': 'second'
                    };
                }
            });

            data['time'] = data_time
            return data;
        }
    })
});



