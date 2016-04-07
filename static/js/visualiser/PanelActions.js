define([
    "dcl/dcl",
    "knockout"
], function (declare, ko, d3, Graph, StixPackage) {
    "use strict";

    return declare(null, {
        declaredClass: "PanelActions",
        constructor: function () {
            this.actions = ko.observableArray([])
        },
        addAction: function(newAction){
            this.actions.push(newAction);
        },
        show_reference_check:function(type) {
            var result = false;
            ko.utils.arrayForEach(this.actions(), function(action) {
                if (action.references()(type)) {
                    result = true;
                }
            })

            return result;
        },
        show_referenced_by_check:function(type) {
           var result = false;
            ko.utils.arrayForEach(this.actions(), function(action) {
                if (action.referenced_by()(type)) {
                    result = true;
                }
            })

            return result;
        }
    })
});
