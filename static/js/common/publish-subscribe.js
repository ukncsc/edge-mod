define([
    "dcl/dcl",
    "knockout",
], function (declare, ko) {
    "use strict";

    return declare(null, {
        declaredClass: "PublishSubscribe",

        constructor: function()
        {
            this.cache = {}
        },

        publish: function (topic, args) {
            // topic: String - The channel to publish on
            // args: Array - The data to publish.
            this.cache[topic] && ko.utils.arrayForEach(this.cache[topic], function (callback) {
                callback.apply({}, args || []);
            });
        },

        subscribe: function (topic, callback) {
            if (!this.cache[topic]) {
                this.cache[topic] = [];
            }
            this.cache[topic].push(callback);
            return [topic, callback]; // Handle to use for unsubscribe
        },

        unsubscribe: function (handle) {
            var topic = handle[0];
            this.cache[topic] && ko.utils.arrayForEach(this.cache[topic], function (callback, idx) {
                if (callback == handle[1]) {
                    this.cache[topic].splice(idx, 1);
                }
            }.bind(this));
        }
    });
});
