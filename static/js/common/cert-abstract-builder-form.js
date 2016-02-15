define([
    "../dcl/dcl",
    "knockout"
], function (declare, ko) {
    "use strict";

    function AbstractBuilderForm (/*String*/ label) {
        this.label = ko.observable(label);
        this.count = ko.observable("");
    }

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
    AbstractBuilderForm.prototype.loadStatic = function (optionLists) {
        // stub - does nothing here

    };

    /*
    Loads/processes data in response to an ajax request
     */
    AbstractBuilderForm.prototype.load = function (data) {
        // stub - does nothing here
    };

    /*
    validates the object's form before save()ing
     */
    AbstractBuilderForm.prototype.doValidation = function () {
        // stub - does nothing here
        return null;
    };

    /*
    Serializes the object in preparation for persistence
     */
    AbstractBuilderForm.prototype.save = function () {
        // stub - does nothing here
        return null;
    };

    return AbstractBuilderForm;
});
