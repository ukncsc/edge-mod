define([], function () {

    postJSON = function (url, obj, callback) {
        if (getJSONReturnError) {
            callback({success:false});
        } else {
            callback({success:true, results:{name: "test-org"}})
        }
    };

});
        var getJSONReturnError = false;
