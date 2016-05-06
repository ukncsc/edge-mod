define([
    "dcl/dcl",
    "knockout"
], function (declare, ko) {
    "use strict";

    function ts(y, M, d, h, m, s) {
        return (new Date(y, M, d, h, m, s)).toLocaleString();
    }

    var defaultFilterText = "status:new";
    var tagDefs = Object.freeze({
        "ATTACK": {label: "ATTACK", colour: "red"},
        "FEED": {label: "Feed", colour: "green"},
        "MESSAGE": {label: "Message", colour: "brown"},
        "REMINDER": {label: "Reminder", colour: "darkcyan"},
        "RESEARCH": {label: "Research", colour: "blue"},
        "SPIKE": {label: "Spike", colour: "orange"},

        "CERT-AU": {label: "CERT-AU", colour: "olive"},
        "CERT-CA": {label: "CERT-CA", colour: "purple"},
        "CERT-EU": {label: "CERT-EU", colour: "navy"},
        "CERT-US": {label: "CERT-US", colour: "black"}
    });
    var mockAlerts = Object.freeze([
        {
            ts: ts(2016, 3, 26, 7, 31, 45),
            status: "new",
            msg: "No updates from CERT-EU for 24 hours",
            source: "FeedCheck",
            tags: ["FEED", "CERT-EU"]
        },
        {
            ts: ts(2016, 3, 25, 21, 23, 9),
            status: "new",
            msg: "Apparent DDOS from 213.173.23.0 subnet",
            source: "RuleEngine",
            tags: ["ATTACK"]
        },
        {
            ts: ts(2016, 3, 25, 20, 45, 55),
            status: "new",
            msg: "7 new file hashes for PIVY malware",
            source: "RuleEngine",
            tags: ["RESEARCH"]
        },
        {
            ts: ts(2016, 3, 25, 17, 25, 13),
            status: "",
            msg: "Check CERT-EU feed tomorrow",
            source: "SelfNote",
            tags: ["REMINDER", "CERT-EU"]
        },
        {
            ts: ts(2016, 3, 25, 16, 11, 2),
            status: "",
            msg: "23 new TOR exit points in UK",
            source: "RuleEngine",
            tags: ["RESEARCH"]
        },
        {
            ts: ts(2016, 3, 25, 14, 4, 56),
            status: "",
            msg: "I'm seeing some new PIVY variants. Have added a new detection rule",
            source: "CTaylor",
            tags: ["MESSAGE"]
        },
        {
            ts: ts(2016, 3, 25, 11, 44, 33),
            status: "",
            msg: ">500 new sightings for 213.173.23.0 subnet",
            source: "RuleEngine",
            tags: ["SPIKE", "CERT-AU"]
        },
        {
            ts: ts(2016, 3, 25, 0, 23, 11),
            status: "",
            msg: ">500 new sightings for 213.173.23.0 subnet",
            source: "RuleEngine",
            tags: ["SPIKE", "CERT-CA"]
        },
        {
            ts: ts(2016, 3, 24, 23, 0, 30),
            status: "",
            msg: "Unable to connect to CERT-US feed",
            source: "FeedCheck",
            tags: ["FEED", "CERT-US"]
        }
    ]);

    function parseFilterText(/*String*/ filterText) {
        var rules = [];
        ko.utils.arrayForEach(filterText.split(/\s+/), function (maybeRule) {
            var ruleParts = maybeRule.split(":", 2);
            var ruleName = ruleParts[0];
            if (["status", "source", "tags"].indexOf(ruleName) !== -1) {
                var ruleValues = ruleParts[1].toLowerCase();
                rules.push({name: ruleName, values: ruleValues.split(",")});
            }
        });
        return rules;
    }

    function hasMatch(/*String[]*/ lookFor, /*Object*/ lookIn) {
        var lookInType = Object.prototype.toString.apply(lookIn).slice(8, -1);
        var matched = false;
        if (lookInType === "Array") {
            for (var i = 0, len = lookIn.length; !matched && i < len; i++) {
                matched = hasMatch(lookFor, lookIn[i]);
            }
        } else {
            matched = lookFor.indexOf(String(lookIn).toLowerCase()) !== -1;
        }
        return matched;
    }

    return declare(null, {
        declaredClass: "AlertModel",
        constructor: function () {
            this.filterText = ko.observable(defaultFilterText);
            this.alerts = ko.computed(function () {
                var filterRules = parseFilterText(this.filterText());
                var numRules = filterRules.length;
                return ko.utils.arrayFilter(mockAlerts, function (anAlert) {
                    var rulesPassed = 0;
                    for (var i = 0; i < numRules; i++) {
                        var rule = filterRules[i];
                        if (hasMatch(rule.values, anAlert[rule.name])) {
                            rulesPassed++;
                        } else {
                            break;
                        }
                    }
                    return rulesPassed === numRules;
                });
            }, this);
        },
        clearSearch: function () {
            this.filterText("");
        },
        loadLog: function () {
            // nothing to do
        },
        tag: function (tagId) {
            return tagDefs[tagId] || {label: tagId, colour: "grey"};
        }
    });
});
