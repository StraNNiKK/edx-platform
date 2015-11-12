;(function (define) {
    'use strict';

    define(['jquery',
            'underscore',
            'common/js/components/views/list',
            'js/dashboard/views/course_view',
            'text!templates/dashboard/courses.underscore'],
        function ($,
                  _,
                  ListView,
                  CourseView,
                  coursesTemplate) {

            var CourseListView = ListView.extend({

                template: _.template(coursesTemplate),

                initialize: function (options) {
                    this.settings = options.settings;
                    this.itemViews = [];
                },

                render: function () {
                    this.$el.html(this.template({courses: this.collection, settings: this.settings}));
                    this.collection.each(this.createItemView, this);

                    return this;
                },

                createItemView: function (course) {
                    var itemView = new CourseView({
                        model: course,
                        settings: this.settings
                    });

                    this.$('.listing-courses').append(itemView.render().el);
                    this.itemViews.push(itemView);
                }
            });

            return CourseListView;
        });

}).call(this, define || RequireJS.define);
