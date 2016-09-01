define([
    "dcl/dcl",
    "knockout"
], function (declare, ko) {
    "use strict";

    return declare(null, {
            declaredClass: "Times",

            constructor: function (saveName, displayName) {
                this.displayName = ko.observable(displayName);
                this.saveName = ko.observable(saveName);
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
        var format = "YYYY-MM-DDTHH:mm:ss"
        $(element).find('input').val(valueAccessor()());
        $(element).datetimepicker({
            format: format,
            useStrict: true,
            keepInvalid: true
        }).on("dp.change", function (ev) {
            if (!ev.date) {
                valueAccessor()("");
            } else if (ev.date.isValid()) {
                valueAccessor()(ev.date.format(format));
            } else {
                valueAccessor()(ev.date._i);
            }
        });
        return ko.bindingHandlers.value.init(element, valueAccessor, allBindingsAccessor, viewModel, bindingContext);
    }
};



