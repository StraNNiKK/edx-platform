;(function (define) {
    'use strict';
    define(['backbone', 'support/js/models/certificate'],
        function(Backbone, CertModel) {
            return Backbone.Collection.extend({
                model: CertModel,

                initialize: function(options) {
                    this.userQuery = options.userQuery || '';
                    this.courseID = options.courseID || '';
                },

                setUserQuery: function(userQuery) {
                    this.userQuery = userQuery;
                },

                setCourseQuery: function(courseQuery) {
                    this.courseID = courseQuery;
                },

                url: function() {
                    var url = '/certificates/search?user_query=' + this.userQuery;
                    if (this.courseID) {
                        url += '&course_id=' + encodeURIComponent(this.courseID);
                    }
                    return url;
                }
            });
    });
}).call(this, define || RequireJS.define);
