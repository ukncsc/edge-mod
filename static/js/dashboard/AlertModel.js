define([
    "dcl/dcl",
    "knockout"
], function (declare, ko) {
    "use strict";

    var defaultFilterText = "status:new";
    var mockNewResults = Object.freeze([
        [(new Date(2016, 3, 26, 7, 31, 45)).toLocaleString(), "*", "No updates from CERT-EU for 24 hours", "FeedCheck", "CERT-EU, FEED"],
        [(new Date(2016, 3, 25, 21, 23, 9)).toLocaleString(), "*", "Apparent DDOS from 213.173.23.0 subnet", "RuleEngine", "ATTACK"],
        [(new Date(2016, 3, 25, 20, 45, 55)).toLocaleString(), "*", "7 new file hashes for PIVY malware", "RuleEngine", "RESEARCH"]
    ]);
    var mockOldResults = Object.freeze([
        [(new Date(2016, 3, 25, 17, 25, 13)).toLocaleString(), "", "Check CERT-EU feed tomorrow", "SelfNote", "CERT-EU, REMINDER"],
        [(new Date(2016, 3, 25, 16, 11, 2)).toLocaleString(), "", "23 new TOR exit points in UK", "RuleEngine", "RESEARCH"],
        [(new Date(2016, 3, 25, 14, 4, 56)).toLocaleString(), "", "I'm seeing some new PIVY variants. Have added a new detection rule", "CTaylor", "MESSAGE"],
        [(new Date(2016, 3, 25, 11, 44, 33)).toLocaleString(), "", ">500 new sightings for 213.173.23.0 subnet", "RuleEngine", "SPIKE, CERT-AU"],
        [(new Date(2016, 3, 25, 0, 23, 11)).toLocaleString(), "", ">500 new sightings for 213.173.23.0 subnet", "RuleEngine", "SPIKE, CERT-CA"],
        [(new Date(2016, 3, 24, 23, 0, 30)).toLocaleString(), "", "Unable to connect to CERT-US feed", "FeedCheck", "CERT-US, FEED"]
    ]);
    var mockAllResults = Object.freeze(mockNewResults.concat(mockOldResults));

    return declare(null, {
        declaredClass: "AlertModel",
        constructor: function () {
            this.filterText = ko.observable(defaultFilterText);
            this.alerts = ko.observableArray(mockNewResults);
        },
        clearSearch: function () {
            this.filterText("");
            this.alerts(mockAllResults);
        },
        loadLog: function () {
            this.filterText(defaultFilterText);
            this.alerts(mockNewResults);
        }
    });
});
