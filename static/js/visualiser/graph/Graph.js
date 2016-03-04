define([
    "dcl/dcl",
    "knockout",
    "d3",
    "./Link",
    "./Node"
], function (declare, ko, d3, Link, Node) {
    "use strict";

    function isGetterSetter(value) {
        return typeof value === "function" && value.length === 1;
    }

    return declare(null, {
        declaredClass: "Graph",
        constructor: function (graphData) {
            var _d3Layout = d3.layout.force();
            this.d3Layout = ko.computed(function () {
                return _d3Layout;
            });
            // create observables for all [gs]etters on _d3Layout with the default value provided by D3
            ko.utils.objectForEach(_d3Layout, function (name, value) {
                if (isGetterSetter(value)) {
                    this[name] = ko.observable(value());
                }
            }.bind(this));
            this.links = ko.observableArray(graphData.links);
            this.nodes = ko.observableArray(graphData.nodes);
        },
        applyBindingValues: function (bindingValues) {
            ko.utils.objectForEach(bindingValues, function (name, value) {
                if (ko.isObservable(this[name])) {
                    this[name](value);
                }
            }.bind(this));
            // set up so that changes in our observables are propagated through to D3
            var _d3Layout = this.d3Layout();
            var _pendingUpdate = null;
            ko.utils.objectForEach(this, function (name, value) {
                if (ko.isObservable(value)) {
                    value.subscribe(function (newValue) {
                        _d3Layout[name](newValue);
                        if (_pendingUpdate) {
                            clearTimeout(_pendingUpdate);
                        }
                        _pendingUpdate = setTimeout(_d3Layout.start.bind(_d3Layout), 50);
                    });
                }
            }.bind(this));
        },
        runModel: function () {
            this.d3Layout().start();

        },
        appendData: function (graphData) {
            //TODO - will need to sort out indexes, etc
        }
    });
});
