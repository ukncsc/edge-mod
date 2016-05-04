define([
    "dcl/dcl",
    "knockout"
], function (declare, ko) {
    "use strict";

    return declare(null, {
        declaredClass: "DashboardModel",
        constructor: function () {
            this.panels = ko.observableArray([
                {label:"Indicators by Type",imageUrl:"chart1.png"},
                {label:"Incidents by Sector",imageUrl:"chart2.png"},
                {label:"Total Objects",imageUrl:"chart3.png"},
                {label:"Duplication",imageUrl:"chart4.png"},
                {label:"Object Count by Source",imageUrl:"chart5.png"},
                {label:"Quality by Source",imageUrl:"chart6.png"},
                {label:"Response Times",imageUrl:"chart7.png"},
                {label:"Observable Types by Source",imageUrl:"chart8.png"},
                {label:"Geographic Spread",imageUrl:"chart9.png"},
                {label:"Incidents by Actor",imageUrl:"chart1.png"},
                {label:"Incidents by TTP",imageUrl:"chart2.png"}
            ]);
        }
    });
});
