define(["knockout-3.1.0", "dcl/dcl"], function (ko, declare) {
    return declare(null, {
        constructor: function() {
            console.log("In ctor(), args=", arguments, ", ko=", ko, ", declare=", declare);
        }
    });
});
