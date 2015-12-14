;(function (define, undefined) {
    'use strict';
    define([
        'gettext', 'jquery', 'underscore', 'common/js/components/views/paginated_view',
        'js/student_profile/views/badge_view', 'js/student_profile/views/badge_list_view'],
        function (gettext, $, _, PaginatedView, BadgeView, BadgeListView) {
            var BadgeListContainer = PaginatedView.extend({
                type: 'badge',
                itemViewClass: BadgeView,
                listViewClass: BadgeListView
            });

            return BadgeListContainer
        });
}).call(this, define || RequireJS.define);