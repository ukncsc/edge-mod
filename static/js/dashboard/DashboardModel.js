define([
    "dcl/dcl",
    "knockout",
    "jquery",
    "gridster",
    "./Panel"
], function (declare, ko, $, gridster, Panel) {
    "use strict";

    return declare(null, {
        declaredClass: "DashboardModel",
        constructor: function () {
            this.panels = ko.observableArray([
                ko.observable(new Panel(1, 1, 2, 2, "Indicators by Type", "chart1.png")),
                ko.observable(new Panel(1, 2, 1, 1, "Incidents by Sector", "chart2.png")),
                ko.observable(new Panel(1, 3, 1, 1, "Total Objects", "chart3.png")),
                ko.observable(new Panel(5, 2, 2, 2, "Geographic Spread",  "geo2.png")),
                ko.observable(new Panel(2, 1, 1, 1, "Hilbert Map",  "hilbert.png")),
                ko.observable(new Panel(2, 2, 1, 1, "Object Count by Source", "chart5.png")),
                ko.observable(new Panel(2, 3, 1, 1, "Quality by Source", "chart6.png")),
                ko.observable(new Panel(4, 2, 1, 2, "Response Times", "chart7.png")),
                ko.observable(new Panel(3, 1, 1, 1, "Observable Types by Source", "chart8.png")),
                ko.observable(new Panel(3, 2, 1, 1, "Incidents by TTP", "chart2.png")),
                ko.observable(new Panel(3, 3, 1, 1, "Duplication", "chart4.png"))
            ]);
        },
        onShow: function () {
            $("#dashboard_main_grid").gridster({
                widget_margins: [6, 6],
                widget_base_dimensions: [250, 225],
                autogrow_cols: true,
                extra_cols: 1,
                resize: {
                    enabled: true,
                    max_size: [3, 3]
                }
            });
        }
    });
});
