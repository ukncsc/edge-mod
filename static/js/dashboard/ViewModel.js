define([
    "dcl/dcl",
    "knockout",
    "./DashboardModel",
    "./AlertModel",
    "./SearchModel",
    "./ConfigurationModel",
    "kotemplate!dashboard:./templates/dashboard.html",
    "kotemplate!alert:./templates/alert.html",
    "kotemplate!search:./templates/search.html",
    "kotemplate!configuration:./templates/configuration.html"
], function (declare, ko, DashboardModel, AlertModel, SearchModel, ConfigurationModel, DashboardTemplate, AlertTemplate,
             SearchTemplate, ConfigurationTemplate) {
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
                {label: "Alerts", template: AlertTemplate.id, model: new AlertModel(), flex: "v"},
                {label: "Search", template: SearchTemplate.id, model: new SearchModel(), flex: "v"},
                {label: "Configure", template: ConfigurationTemplate.id, model: new ConfigurationModel(), flex: "h"}
            ]);
            this.selectedFolder = ko.observable(this.folders.peek()[0]);
        }
    });
});
