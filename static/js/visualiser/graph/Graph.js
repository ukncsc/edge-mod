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
            // create proxy observables for all [gs]etters on _d3Layout with the default value provided by D3
            var _pendingUpdate = null;
            ko.utils.objectForEach(_d3Layout, function (name, value) {
                if (isGetterSetter(value)) {
                    var proxy = ko.observable(value());
                    proxy.subscribe(function (newValue) {
                        _d3Layout[name](newValue);
                        if (_pendingUpdate) {
                            clearTimeout(_pendingUpdate);
                        }
                        _pendingUpdate = setTimeout(_d3Layout.start.bind(_d3Layout), 100);
                    });
                    this[name] = proxy;
                }
            }.bind(this));
            this.links(ko.utils.arrayMap(graphData.links, function (linkData) {
                return new Link(linkData);
            }));
            this.nodes(ko.utils.arrayMap(graphData.nodes, function (nodeData) {
                return new Node(nodeData);
            }));
            this.selectedNode = ko.observable(null);
        },
        applyBindingValues: function (bindingValues) {
            ko.utils.objectForEach(bindingValues, function (name, value) {
                if (ko.isObservable(this[name])) {
                    this[name](value);
                }
            }.bind(this));
        },
        selectNode: function (nodeId) {
            var oldNode = this.selectedNode();
            if (oldNode instanceof Node) {
                oldNode.isSelected(false);
            }
            var newNode = this.nodes().filter(function (node) {
                if (nodeId === node.id()) {
                    return node;
                }
            })[0];
            if (newNode instanceof Node) {
                newNode.isSelected(true);
                this.selectedNode(newNode);
            }
        },
        appendData: function (graphData) {
            //TODO - will need to sort out indexes, etc
        }
    });
});
