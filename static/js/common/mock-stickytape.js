define([], function () {

    getJSON = function (url, obj, success, error) {
        if (getJSONReturnError) {
            error({});
        }
        else {
            success({name: "test-org"});
        }
    };

});
        var getJSONReturnError = false;
