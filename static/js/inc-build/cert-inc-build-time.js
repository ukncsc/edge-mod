define([
    "dcl/dcl",
    "knockout",
    "common/jquery-shim"
], function (declare, ko, $) {
    "use strict";

    return declare(null, {
            declaredClass: "Times",

            constructor: function (save_name, visible_name) {
                this.type_name = ko.observable(visible_name);
                this.save_name = ko.observable(save_name);
                this.time_string = ko.observable("");
            },

            load: function(data) {
                if (typeof data === "string") {
                    this.time_string(data);
                } else {
                    this.time_string(data['value']);
                }
            }
        }
    );
});

ko.bindingHandlers.dateTime = {
     init: function (element, valueAccessor, allBindingsAccessor, viewModel, bindingContext) {
            $(element).datetimepicker({format: "YYYY-MM-DD HH:mm:ss", defaultDate:valueAccessor()()}).on("dp.change", function (ev) {
                var observable = valueAccessor();
                observable(ev.date.format("YYYY-MM-DDTHH:mm:ss"));
            });
            return ko.bindingHandlers.value.init(element, valueAccessor, allBindingsAccessor, viewModel, bindingContext);
        }
};



