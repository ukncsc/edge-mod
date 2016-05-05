define([
    "dcl/dcl",
    "knockout"
], function (declare, ko) {
    "use strict";

    var defaultSearchText = "after:16/04/2016 before:26/04/2016 match:stixtype:=:obs match:namespace:=:certuk";
    var mockResults = Object.freeze([
        [(new Date(2016, 3, 26)).toLocaleDateString(), "obs", "Crouching_Powerpoint_Hidden_Trojan_24C3.pdf", "certuk", "WHITE"],
        [(new Date(2016, 3, 25)).toLocaleDateString(), "obs", "Beijings-rising-hackers.pdf", "certuk", "WHITE"],
        [(new Date(2016, 3, 24)).toLocaleDateString(), "obs", "Exile.doc", "certuk", "WHITE"],
        [(new Date(2016, 3, 23)).toLocaleDateString(), "obs", "Deibert.pdf", "certuk", "WHITE"],
        [(new Date(2016, 3, 22)).toLocaleDateString(), "obs", "lingshui.htm", "certuk", "WHITE"],
        [(new Date(2016, 3, 21)).toLocaleDateString(), "obs", "diary.html", "certuk", "WHITE"],
        [(new Date(2016, 3, 20)).toLocaleDateString(), "obs", "government-and.html", "certuk", "WHITE"],
        [(new Date(2016, 3, 19)).toLocaleDateString(), "obs", "AR2008032102605.html", "certuk", "WHITE"],
        [(new Date(2016, 3, 18)).toLocaleDateString(), "obs", "bg_2106.pdf", "certuk", "WHITE"],
        [(new Date(2016, 3, 17)).toLocaleDateString(), "obs", "zeus-crimeware-kit-gets-carding-layout.html", "certuk", "WHITE"],
        [(new Date(2016, 3, 16)).toLocaleDateString(), "obs", "msg00086.html", "certuk", "WHITE"],
    ]);

    return declare(null, {
        declaredClass: "SearchModel",
        constructor: function () {
            this.searchText = ko.observable(defaultSearchText);
            this.columns = ko.observableArray([
                "Date",
                "Type",
                "Title",
                "Namespace",
                "TLP"
            ]);
            this.rowdata = ko.observableArray(mockResults);
        },
        clearSearch: function () {
            this.searchText("");
            this.rowdata([]);
        },
        loadLog: function () {
            this.searchText(defaultSearchText);
            this.rowdata(mockResults);
        }
    });
});
