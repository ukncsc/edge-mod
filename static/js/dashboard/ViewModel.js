define([
    "dcl/dcl",
    "knockout",
    "./DashboardModel",
    "./AlertModel",
    "./SearchModel",
    "kotemplate!dashboard:./templates/dashboard.html",
    "kotemplate!alert:./templates/alert.html",
    "kotemplate!search:./templates/search.html"
], function (declare, ko, DashboardModel, AlertModel, SearchModel, DashboardTemplate, AlertTemplate,
             SearchTemplate) {
    "use strict";

    return declare(null, {
        declaredClass: "ViewModel",
        constructor: function () {
            this.folders = ko.observableArray([
                {
                    label: "Dashboard",
                    template: DashboardTemplate.id,
                    model: new DashboardModel(),
                    flex: "v"
                },
                {label: "Search", template: SearchTemplate.id, model: new SearchModel(), flex: "v"},
                {label: "Alerts", template: AlertTemplate.id, model: new AlertModel(), flex: "v"}
            ]);
            this.selectedFolder = ko.observable(this.folders.peek()[0]);
            this.savedQueries = ko.observableArray([
                {value:0, label:"Indicators by Type"},
                {value:1, label:"Incidents by Type"},
                {value:2, label:"Observables by Country"},
                {value:3, label:"Feed Item Count by Provider"}
            ]);
            this.visualisationTypes = ko.observableArray([
                {label: "Line Graph", imageUrl: "chart2.png"},
                {label: "Pie Chart", imageUrl: "chart3.png"},
                {label: "Vertical Bar", imageUrl: "chart8.png"},
                {label: "Horizontal Bar", imageUrl: "chart1.png"},
                {label: "X-Y Scatter", imageUrl: "chart6.png"},
                {label: "Stacked X-Y Area", imageUrl: "chart5.png"},
                {label: "X-Y Spread", imageUrl: "chart4.png"},
                {label: "X-Y Ranged 1", imageUrl: "chart7.png"},
                {label: "X-Y Ranged 2", imageUrl: "chart9.png"}
            ]);
        },
        selectByLabel: function (label) {
            this.selectedFolder(ko.utils.arrayFirst(this.folders.peek(), function (folder) {
                return folder.label === label;
            }));
        }
    });
});
