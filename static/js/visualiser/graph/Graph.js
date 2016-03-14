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
            this.nodes(ko.utils.arrayMap(graphData.nodes, function (nodeData) {
                return new Node(nodeData);
            }));
            var /*Node[]*/ _rawNodes = this.nodes.peek();
            this.links(ko.utils.arrayMap(graphData.links, function (linkData) {
                return new Link(_rawNodes[linkData.source], _rawNodes[linkData.target]);
            }.bind(this)));
            this.selectedNode = ko.observable(null);
            this.selectedLinkedNodes = ko.computed(function () {
                var selectedNode = this.selectedNode();
                var linkedNodes = {
                    parentOf: [],
                    childOf: []
                };
                ko.utils.arrayForEach(this.nodes(), function (node) {
                    node.isRelated(false);
                });
                if (selectedNode instanceof Node) {
                    var findIndex = selectedNode.index;
                    ko.utils.arrayForEach(this.links(), function (link) {
                        if (link.source.index === findIndex) {
                            linkedNodes.parentOf.push(link.target);
                            link.target.isRelated(true);
                        }
                        if (link.target.index === findIndex) {
                            linkedNodes.childOf.push(link.source);
                            link.source.isRelated(true);
                        }
                    });
                }
                return linkedNodes;
            }, this).extend({rateLimit: 50});
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
