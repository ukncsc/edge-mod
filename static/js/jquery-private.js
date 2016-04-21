var old = window['$'];
define(['jquery'], function (jq) {
    var jq_res = jq.noConflict( true );
    window['$'] = window['jQuery'] = old;
    return jq_res;
});
