define([
    "dcl/dcl",
    "knockout"
], function (declare, ko) {
    "use strict";


    var Time = declare(null, {
        declaredClass: "Times",

        constructor: function () {
            this.type = ko.observable("type1");
            this.time_timezone = ko.observable("zone1");
            this.date = ko.observable("adate")
            this.hours = ko.observable("hours")
            this.minutes = ko.observable("minutes")
            this.seconds = ko.observable("seconds")
            this.timezone = ko.observable("zone1")
                },


            }
        )
    return Time;
    });



