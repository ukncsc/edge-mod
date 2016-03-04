define([
    "knockout",
    "d3",
    "jquery"
], function (ko, d3, $) {
    "use strict";

    function sizeToParent(element) {
        var parent = $(element.parentNode);
        var height = parent.height();
        var width = parent.width();
        d3.select(element)
            .attr("viewBox", "0 0 " + width + " " + height)
            .attr("height", height)
            .attr("width", width);
    }

    ko.bindingHandlers.forceGraph = {
        init: function (element, valueAccessor, allBindings, viewModel, bindingContext) {
            // This will be called when the binding is first applied to an element
            // Set up any initial state, event handlers, etc. here
            if (!(element.tagName === "svg")) {
                throw new Error("The 'forceGraph' binding can only be applied to 'svg' elements.");
            }
            if (!(element.firstElementChild && element.firstElementChild.tagName === "g")) {
                throw new Error("The node template must be a 'g' element.");
            }
            d3.select(window).on("resize", function () {
                sizeToParent(element);
            });
            sizeToParent(element);

            var graphModel = valueAccessor()();
            graphModel.applyBindingValues(allBindings());

            // Tell Knockout that we've already dealt with child bindings
            return {
                controlsDescendantBindings: true
            }
        },
        update: function (element, valueAccessor, allBindings, viewModel, bindingContext) {
            // This will be called once when the binding is first applied to an element,
            // and again whenever any observables/computeds that are accessed change
            // Update the DOM element based on the supplied values here.
        }
    };
});
