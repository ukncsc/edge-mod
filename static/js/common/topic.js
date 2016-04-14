define([
    "knockout"
], function (ko) {
    "use strict";

    var subscriptions = {};

    return Object.freeze({
        /**
         * Publishes a message to a topic on the pub/sub hub.
         * @param topic The name of the topic to publish to
         * @param message An message to distribute to the topic listeners
         */
        publish: function (/*String*/ topic, /*Object*/ message) {
            if (topic in subscriptions) {
                ko.utils.arrayForEach(subscriptions[topic], function (callback) {
                    setTimeout(callback.listener.apply(callback.scope, [message]), 0);
                });
            }
        },

        /**
         * Subscribes to a topic on the pub/sub hub
         * @param topic The topic to subscribe to
         * @param listener A function to call when a message is published to the given topic
         * @param scope The scope in which to call `listener`
         * @returns Object handle with a `remove()` function
         */
        subscribe: function (/*String*/ topic, /*function*/ listener, /*Object?*/ scope) {
            if (!(subscriptions.hasOwnProperty(topic))) {
                subscriptions[topic] = [];
            }
            var topicSubscriptions = subscriptions[topic];
            var subscription = Object.freeze({
                listener: listener,
                scope: scope
            });
            topicSubscriptions.push(subscription);
            return {
                remove: function () {
                    ko.utils.arrayRemoveItem(topicSubscriptions, subscription);
                    if (topicSubscriptions.length === 0) {
                        delete subscriptions[topic];
                    }
                    topicSubscriptions = subscription = null;
                }
            };
        }
    });
});
