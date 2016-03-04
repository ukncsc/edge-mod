define([
    "dcl/dcl",
    "knockout",
    "d3",
    "./Link",
    "./Node"
], function (declare, ko, d3, Link, Node) {
    "use strict";

    return declare(null, {
        declaredClass: "Graph",
        constructor: function (graphData) {
            this.links = ko.observableArray(graphData.links);
            this.nodes = ko.observableArray(graphData.nodes);

            var _d3Layout = d3.layout.force();
            this.d3Layout = ko.computed(function () {
                return _d3Layout;
            });
console.log("D3:", _d3Layout);
            ko.utils.objectForEach(_d3Layout, function (name, value) {
                if (name === "links" || name === "nodes") {
                    return;
                }
                if (typeof value === "function" && value.length === 1) {
                    this[name] = ko.observable(value());
                }
            }.bind(this));
console.log(this);
        },
        applyBindingValues: function (bindingValues) {
            ko.utils.objectForEach(bindingValues, function (name, value) {
                if (ko.isObservable(this[name])) {
                    this[name](value);
                }
            }.bind(this));
        },
        appendData: function (graphData) {
            //TODO - will need to sort out indexes, etc
        }
    });
});
