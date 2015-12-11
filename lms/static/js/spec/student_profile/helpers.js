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

    var exampleBadges = {
        "count": 3,
        "previous": null,
        "num_pages": 1,
        "results": [{
            "badge_class": {
                "slug": "test_slug_0_0753941808621",
                "issuing_component": "test_component",
                "display_name": "Test Badge",
                "course_id": null,
                "description": "Yay! It's a test badge.",
                "criteria": "https://example.com/syllabus",
                "image_url": "http://localhost:8000/media/badge_classes/test_lMB9bRw.png"
            },
            "image_url": "http://example.com/image.png",
            "assertion_url": "http://example.com/example.json",
            "created_at": "2015-12-03T16:25:57.676113Z"
        }, {
            "badge_class": {
                "slug": "test_slug_0_978058171531",
                "issuing_component": "test_component",
                "display_name": "Test Badge",
                "course_id": null,
                "description": "Yay! It's a test badge.",
                "criteria": "https://example.com/syllabus",
                "image_url": "http://localhost:8000/media/badge_classes/test_YMRswqm.png"
            },
            "image_url": "http://example.com/image.png",
            "assertion_url": "http://example.com/example.json",
            "created_at": "2015-12-03T16:25:58.904203Z"
        }, {
            "badge_class": {
                "slug": "test_slug_0_851200237578",
                "issuing_component": "test_component",
                "display_name": "Test Badge",
                "course_id": null,
                "description": "Yay! It's a test badge.",
                "criteria": "https://example.com/syllabus",
                "image_url": "http://localhost:8000/media/badge_classes/test_Z4sKJDu.png"
            },
            "image_url": "http://example.com/image.png",
            "assertion_url": "http://example.com/example.json",
            "created": "2015-12-03T16:25:59.316850Z"
    }]};

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
        exampleBadges: exampleBadges, emptyBadges: emptyBadges
    };
});
