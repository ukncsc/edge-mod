define([
    "dcl/dcl",
    "knockout",
    "common/cert-abstract-builder-form",
    "inc-build/cert-inc-build-time"
], function (declare, ko, AbstractBuilderForm, Time) {
    "use strict";

    return declare(AbstractBuilderForm, {
        declaredClass: "TimePanel",

        constructor: declare.superCall(function (sup) {
            return function () {
                this.timeTypes = ko.observableArray();
                sup.call(this, "Times");
            }
        }),

        counter: function () {
            var count = 0;
            ko.utils.arrayForEach(this.timeTypes(), function (timeType) {
                if (timeType.timeString() != "") {
                    count++;
                }
            });
            return count != 0 ? count : "";
        },

        loadStatic: function (optionsList) {
            this.timeTypes.removeAll();
            for (var i = 0; i < optionsList['time_types_list'].length; i++) {
                this.timeTypes.push(new Time(optionsList['time_types_list'][i][0], optionsList['time_types_list'][i][1]));
            }
        },

        load: function (data) {
            var self = this;
            ko.utils.arrayForEach(self.timeTypes(), function (timeType) {
                timeType.load("");
            });


            if ('time' in data) {
                ko.utils.objectForEach(data['time'], function (i, v) {
                    ko.utils.arrayForEach(self.timeTypes(), function (timeType) {
                        if (timeType.saveName() === i) {
                            timeType.load(v);
                        }
                    });
                });
            }
        },

        save: function () {
            var dataTime = {};
            ko.utils.arrayForEach(this.timeTypes(), function (item) {
                if (item.timeString() != "") {
                    dataTime[item.saveName()] = {
                        'value': item.timeString(),
                        'precision': 'second' //Hardcoded for now and strictly not needed for 'second'.
                    };
                }
            });

            var data = {};
            data['time'] = dataTime
            return data;
        }
    })
});



