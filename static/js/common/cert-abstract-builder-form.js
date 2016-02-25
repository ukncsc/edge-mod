define([
    "../dcl/dcl",
    "knockout",
    "common/cert-messages",
], function (declare, ko, Messages) {
    "use strict";

    var AbstractBuilderForm = declare(null, {

        declaredClass: "AbstractBuilderForm",
        constructor: function (labelIn) {
            this.label = ko.observable(labelIn);
            this.count = ko.observable("");
            this.validationGroup = ko.observableArray();
        },

        /*
         Loads 'static' content i.e. content that was assigned to a variable
         via an inline script in a server-side template.

         Example from ind-build.js :
         <script>
         ...
         incident_builder.tlps_list = {{ tlps|safe }};
         ...
         </script>
         */
        loadStatic: function (optionLists) {
            // stub - does nothing here

        },

        /*
         Loads/processes data in response to an ajax request
         */
        load: function (data) {
            // stub - does nothing here
        },

        /*
         validates the object's form before save()ing
         */
        doValidation: function () {
            var msgs = new Messages();
            ko.utils.arrayForEach(this.validationGroup(), function (validatable_obs) {
                if (validatable_obs.hasError()) {
                    msgs.addError(validatable_obs.displayErrorMessage());
                }
            });


            return msgs;

        },

        /*
         Serializes the object in preparation for persistence
         */
        save: function () {
            // stub - does nothing here
            return null;
        },
    });

    return AbstractBuilderForm;
});
