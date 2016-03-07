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
            return function (pubsub) {
                this.timeTypes = ko.observableArray();
                this.timeZone = ko.observable();
                sup.call(this, "Times");
                pubsub.subscribe('status_changed', function (data) {
                    if (data === 'Closed') {
                        postJSON("/adapter/certuk_mod/ajax/get_datetime/", {}, function (result) {
                            this.set_closed_time(result['result']);
                        }.bind(this));
                    } else {
                        this.set_closed_time("");
                    }
                }.bind(this));
            }
        }),

        set_closed_time: function (timeStr) {
            this.set_time(timeStr, 'incident_closed')
        },

        set_opened_time: function (timeStr) {
            this.set_time(timeStr, 'incident_opened')
        },

        set_time: function (timeStr, name) {
            ko.utils.arrayForEach(this.timeTypes(), function (timeType) {
                if (timeType.saveName() === name) {
                    timeType.load(timeStr);
                }
            });
        },

        counter: function () {
            var count = 0;
            ko.utils.arrayForEach(this.timeTypes(), function (timeType) {
                if (timeType.timeString() != "") {
                    count++;
                }
            });
            return count != 0 ? count : "";
        },

        loadTimeType: function (timeInfo) {
            var displayName = timeInfo[1]

            var newTime = new Time(
                timeInfo[0],
                displayName
            )

            newTime.timeString.extend({
                requiredGrouped: {
                    required: timeInfo[2],
                    group: this.validationGroup,
                    displayMessage: displayName + " time is required for your indicator"
                }
            })
            this.timeTypes.push(newTime);
        },

        loadStatic: function (optionsList) {
            this.timeZone = optionsList['time_zone']
            this.timeTypes.removeAll();
            for (var i = 0; i < optionsList['time_types_list'].length; i++) {
                this.loadTimeType(optionsList['time_types_list'][i])
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
            } else {
                postJSON("/adapter/certuk_mod/ajax/get_datetime/", {}, function (result) {
                    this.set_opened_time(result['result']);
                }.bind(this));
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





