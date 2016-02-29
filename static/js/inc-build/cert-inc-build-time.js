define([
    "dcl/dcl",
    "knockout",
    "common/jquery-shim"
], function (declare, ko, $) {
    "use strict";

    return declare(null, {
            declaredClass: "Times",

            constructor: function (save_name, displayName) {
                this.displayName = ko.observable(displayName);
                this.saveName = ko.observable(save_name);
                this.timeString = ko.observable("");
            },

            load: function (data) {
                //The backend encodes times differently depending on whether they contain non-second precision.
                this.timeString(typeof data === "string" ? data : data['value']);
            }
        }
    );
});

ko.bindingHandlers.dateTime = {
    init: function (element, valueAccessor, allBindingsAccessor, viewModel, bindingContext) {
        $(element).datetimepicker({
            format: "YYYY-MM-DD HH:mm:ss",
            defaultDate: valueAccessor()()
        }).on("dp.change", function (ev) {
            valueAccessor()(ev.date?ev.date.format("YYYY-MM-DDTHH:mm:ss"): "");
        });
        return ko.bindingHandlers.value.init(element, valueAccessor, allBindingsAccessor, viewModel, bindingContext);
    }
};



