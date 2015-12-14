define(['underscore'], function(_) {
    'use strict';

    var expectProfileElementContainsField = function(element, view) {
        var $element = $(element);
        var fieldTitle = $element.find('.u-field-title').text().trim();

        if (!_.isUndefined(view.options.title)) {
            expect(fieldTitle).toBe(view.options.title);
        }

        if ('fieldValue' in view || 'imageUrl' in view) {
            if ('imageUrl' in view) {
                expect($($element.find('.image-frame')[0]).attr('src')).toBe(view.imageUrl());
            } else if (view.fieldValue()) {
                expect(view.fieldValue()).toBe(view.modelValue());

            } else if ('optionForValue' in view) {
                expect($($element.find('.u-field-value .u-field-value-readonly')[0]).text()).toBe(view.displayValue(view.modelValue()));

            }else {
                expect($($element.find('.u-field-value .u-field-value-readonly')[0]).text()).toBe(view.modelValue());
            }
        } else {
            throw new Error('Unexpected field type: ' + view.fieldType);
        }
    };

    var expectProfilePrivacyFieldTobeRendered = function(learnerProfileView, othersProfile) {

        var accountPrivacyElement = learnerProfileView.$('.wrapper-profile-field-account-privacy');
        var privacyFieldElement = $(accountPrivacyElement).find('.u-field');

        if (othersProfile) {
            expect(privacyFieldElement.length).toBe(0);
        } else {
            expect(privacyFieldElement.length).toBe(1);
            expectProfileElementContainsField(privacyFieldElement, learnerProfileView.options.accountPrivacyFieldView);
        }
    };

    var expectSectionOneTobeRendered = function(learnerProfileView) {

        var sectionOneFieldElements = $(learnerProfileView.$('.wrapper-profile-section-one')).find('.u-field');

        expect(sectionOneFieldElements.length).toBe(4);
        expectProfileElementContainsField(sectionOneFieldElements[0], learnerProfileView.options.profileImageFieldView);
        expectProfileElementContainsField(sectionOneFieldElements[1], learnerProfileView.options.usernameFieldView);

        _.each(_.rest(sectionOneFieldElements, 2) , function (sectionFieldElement, fieldIndex) {
            expectProfileElementContainsField(
                sectionFieldElement,
                learnerProfileView.options.sectionOneFieldViews[fieldIndex]
            );
        });
    };

    var expectSectionTwoTobeRendered = function(learnerProfileView) {

        var sectionTwoElement = learnerProfileView.$('.wrapper-profile-section-two');
        var sectionTwoFieldElements = $(sectionTwoElement).find('.u-field');

        expect(sectionTwoFieldElements.length).toBe(learnerProfileView.options.sectionTwoFieldViews.length);

         _.each(sectionTwoFieldElements, function (sectionFieldElement, fieldIndex) {
            expectProfileElementContainsField(
                sectionFieldElement,
                learnerProfileView.options.sectionTwoFieldViews[fieldIndex]
            );
        });
    };

    var expectProfileSectionsAndFieldsToBeRendered = function (learnerProfileView, othersProfile) {
        expectProfilePrivacyFieldTobeRendered(learnerProfileView, othersProfile);
        expectSectionOneTobeRendered(learnerProfileView);
        expectSectionTwoTobeRendered(learnerProfileView);
    };

    var expectLimitedProfileSectionsAndFieldsToBeRendered = function (learnerProfileView, othersProfile) {
        expectProfilePrivacyFieldTobeRendered(learnerProfileView, othersProfile);

        var sectionOneFieldElements = $(learnerProfileView.$('.wrapper-profile-section-one')).find('.u-field');

        expect(sectionOneFieldElements.length).toBe(2);
        expectProfileElementContainsField(
            sectionOneFieldElements[0],
            learnerProfileView.options.profileImageFieldView
        );
        expectProfileElementContainsField(
            sectionOneFieldElements[1],
            learnerProfileView.options.usernameFieldView
        );

        if (othersProfile) {
            expect($('.profile-private--message').text())
                .toBe('This edX learner is currently sharing a limited profile.');
        } else {
            expect($('.profile-private--message').text()).toBe('You are currently sharing a limited profile.');
        }
    };

    var expectProfileSectionsNotToBeRendered = function(learnerProfileView) {
        expect(learnerProfileView.$('.wrapper-profile-field-account-privacy').length).toBe(0);
        expect(learnerProfileView.$('.wrapper-profile-section-one').length).toBe(0);
        expect(learnerProfileView.$('.wrapper-profile-section-two').length).toBe(0);
    };

    var expectModeToggleToBeHidden = function(requests, modeToggleView) {
        // Unrelated initial request, no badge request
        expect(requests.length).toBe(1);
        expect(modeToggleView.$el.is(':visible')).toBe(false);
    };

    var expectModeToggleToBeShown = function(modeToggleView) {
        expect(modeToggleView.$el.is(':visible')).toBe(true);
    };

    var expectBadgesDisplayed = function(badgeListingView, learnerProfileView, empty) {
        expect(learnerProfileView.$el.find('.wrapper-profile-section-two').is(':visible')).toBe(false);
        expect(badgeListingView.$el.is(':visible')).toBe(true);
        console.log(badgeListingView.$el.find('.badge-display'));
        console.log(badgeListingView.$el);
        debugger;
        if (empty) {
            expect(badgeListingView.$el.find('.badge-display').length).toBe(1);
        } else {
            expect(badgeListingView.$el.find('.badge-display').length).toBe(4);
        }
        expect(badgeListingView.$el.find('.find-button-container').length).toBe(1);
    };

    var expectBadgesHidden = function(badgeListingView, learnerProfileView) {
        expect(badgeListingView.$el.is(':visible')).toBe(false);
        expect(learnerProfileView.$el.find('.wrapper-profile-section-two').is(':visible')).toBe(true);
    };

    var expectPage = function(badgeListContainer, pageData) {
        var index = badgeListContainer.$el.find('div.search_tools span');
        expect(index.text()).toBe("Showing "  + pageData.start + "-" + pageData.start + pageData.results.length +
            "out of " + pageData.count + " total ");
        expect(badgeListContainer.$el.find('.current-page').text()).toBe("" + pageData.current_page);
        _.each(pageData.results, function(badge) {
            expect($(":contains(" + badge.name + ")").length).toBe(1)
        })
    };

    var firstPageBadges = {
        count: 53,
        previous: null,
        next: "/arbitrary/url",
        num_pages: 6,
        start: 0,
        current_page: 1,
        results: []
    };

    var secondPageBadges = {
        count: 53,
        previous: "/arbitrary/url",
        next: "/arbitrary/url",
        num_pages: 6,
        start: 10,
        current_page: 2,
        results: []
    };

    var thirdPageBadges = {
        count: 53,
        previous: "/arbitrary/url",
        next: null,
        start: 20,
        current_page: 3,
        results: []
    };

    function makeBadge (num) {
        return {
            "badge_class": {
                "slug": "test_slug_" + num,
                "issuing_component": "test_component",
                "display_name": "Test Badge " + num,
                "course_id": null,
                "description": "Yay! It's a test badge.",
                "criteria": "https://example.com/syllabus",
                "image_url": "http://localhost:8000/media/badge_classes/test_lMB9bRw.png"
            },
            "image_url": "http://example.com/image.png",
            "assertion_url": "http://example.com/example.json",
            "created_at": "2015-12-03T16:25:57.676113Z"
        }
    }

    _.each(_.range(0, 10), function(i) {
        firstPageBadges.results.push(makeBadge(i))
    });

    _.each(_.range(10, 20), function(i) {
        secondPageBadges.results.push(makeBadge(i))
    });

    _.each(_.range(20, 30), function(i) {
        thirdPageBadges.results.push(makeBadge(i))
    });

    var emptyBadges = {
        "count": 0,
        "previous": null,
        "num_pages": 1,
        "results": []
    };

    return {
        expectLimitedProfileSectionsAndFieldsToBeRendered: expectLimitedProfileSectionsAndFieldsToBeRendered,
        expectProfileSectionsAndFieldsToBeRendered: expectProfileSectionsAndFieldsToBeRendered,
        expectProfileSectionsNotToBeRendered: expectProfileSectionsNotToBeRendered,
        expectModeToggleToBeHidden: expectModeToggleToBeHidden, expectModeToggleToBeShown: expectModeToggleToBeShown,
        expectBadgesDisplayed: expectBadgesDisplayed, expectBadgesHidden: expectBadgesHidden,
        firstPageBadges: firstPageBadges, secondPageBadges: secondPageBadges, thirdPageBadges: thirdPageBadges,
        emptyBadges: emptyBadges, expectPage: expectPage
    };
});
