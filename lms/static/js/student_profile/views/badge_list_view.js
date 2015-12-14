;(function (define, undefined) {
    'use strict';
    define([
            'gettext', 'jquery', 'underscore', 'common/js/components/views/list', 'js/student_profile/views/badge_view',
            'text!templates/student_profile/badge_placeholder.underscore'],
        function (gettext, $, _, ListView, BadgeView, badgePlaceholder) {
            var BadgeListView = ListView.extend({
                'tagName': 'div',
                renderCollection: function () {
                    this.$el.html('');
                    var row = $('<div class="row">');
                    var append_placeholder = ! this.collection.hasNextPage();
                    var make_last_row = true;
                    // Split into two columns.
                    this.collection.each(function (badge, index) {
                        /*jshint -W018 */
                        var make_row = (index && !(index % 2));
                        if (make_row) {
                            this.$el.append(row);
                            row = $('<div class="row">');
                            make_last_row = false;
                        } else {
                            make_last_row = true;
                        }
                        var item = new BadgeView({model: badge}).render().el;
                        row.append(item);
                        this.itemViews.push(item)
                    }, this);
                    // Placeholder must always be at the end, and may need a new row.
                    var placeholder = _.template(
                        badgePlaceholder,  {find_courses_url: this.options.find_courses_url}
                    );
                    if (! append_placeholder) {
                        return;
                    }
                    if (make_last_row) {
                        this.$el.append(row);
                        row = $('<div class="row">');
                    }
                    row.append(placeholder);
                    this.$el.append(row);
                    return this;
                }
            });

            return BadgeListView;
        });
}).call(this, define || RequireJS.define);
