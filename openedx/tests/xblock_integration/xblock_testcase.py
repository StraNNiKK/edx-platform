from collections import namedtuple

import unittest

from django.conf import settings
from django.core.urlresolvers import reverse

from xmodule.modulestore.tests.django_utils import SharedModuleStoreTestCase
from xmodule.modulestore.tests.factories import CourseFactory, ItemFactory

from lms.djangoapps.courseware.tests.helpers import LoginEnrollmentTestCase
from student.roles import GlobalStaff

class XBlockTestCase(SharedModuleStoreTestCase, LoginEnrollmentTestCase):
    STUDENTS = [
        ('alice@sender.org', 'foo', False),
        ('eve@listener.org', 'bar', False),
        ('bob@receiver.org', 'baz', True),
    ]

    urls = {}

    @classmethod
    def setUpClass(cls):
        '''
        Unless overridden, we create two student users and one staff
        user. We create the course hierarchy based on the OLX defined
        in the XBlock test class. Until we can deal with OLX, that 
        actually will come from a list.
        '''
        # Nose runs setUpClass methods even if a class decorator says to skip
        # the class: https://github.com/nose-devs/nose/issues/946
        # So, skip the test class here if we are not in the LMS.
        if settings.ROOT_URLCONF != 'lms.urls':
            raise unittest.SkipTest('Test only valid in lms')

        super(XBlockTestCase, cls).setUpClass()

        cls.setupScenario()

    def setup(self):
        super(XBlockTestCase, self).setUp()
        self.setupUsers()

    def setupUsers(self):
        for (email, password, staff) in self.STUDENTS:
            self.login(email, password)
            self.enroll(self.course, verify=True)

    @classmethod
    def setupScenario(cls):
        cls.course = CourseFactory.create(
            display_name='Test_Course'
        )

        cls.chapter = ItemFactory.create(
            parent=cls.course,
            display_name='Overview',
            category='chapter'
        )

        cls.urls = {}

        with cls.store.bulk_operations(cls.course.id, emit_signals=False):
            for section in cls.test_configuration:
                section_item = ItemFactory.create(
                    parent=cls.chapter,
                    display_name=section['urlname'],
                    category='sequential'
                )

                cls.urls[section['urlname']] = reverse(
                    'courseware_section',
                    kwargs={
                        'course_id': unicode(cls.course.id),
                        'chapter': 'Overview',
                        'section': section['urlname'],
                    }
                )
                print section['urlname']
                print cls.urls[section['urlname']]

                blocks = section["xblocks"]

                unit_item = ItemFactory.create(
                    parent=section_item,
                    display_name="unit_"+section['urlname'],
                    category='vertical'
                )
                for block in blocks:
                    block_item = ItemFactory.create(
                        parent=unit_item,
                        category=block['blocktype'],
                        display_name=block['urlname']
                    )
            cls.course_url = reverse(
                'courseware_section',
                kwargs={
                    'course_id': unicode(cls.course.id),
                    'chapter': 'Overview',
                    'section': section['urlname'],
                }
            )
            print cls.course_url

            cls.course_url = reverse(
                'courseware_section',
                kwargs={
                    'course_id': unicode(cls.course.id),
                    'chapter': u'Overview',
                    'section': u'two_done_block_test',
                }
            )
            print cls.course_url

    def _containing_section(self, block_urlname):
        '''
        For a given block, return the parent section
        '''
        for section in self.test_configuration:
            blocks = section["xblocks"]
            for block in blocks:
                if block['urlname'] == block_urlname:
                    return section['urlname']
        raise Exception("Block not found "+block_urlname)

    def assertXBlockScreenshot(self, block_urlname, rendering=None):
        '''
        As in Bok Choi, but instead of a CSS selector, we pass a
        block_id. We may want to be able to pass an optional selector
        for picking a subelement of the block.

        This confirms status code, and that the screenshot is
        identical.

        TODO: IMPLEMENT
        '''
        pass

    def get_handler_url(self, handler, xblock_name=None):
        """
        Get url for the specified xblock handler
        """
        key = unicode(self.course.id.make_usage_key('done', xblock_name))
        print key
        return reverse('xblock_handler', kwargs={
            'course_id': unicode(self.course.id),
            'usage_id': key,
            'handler': handler,
            'suffix': ''
        })

    def ajax(self, function, block_urlname, json_data):
        '''
        Call a json_handler in the XBlock. Return the response as
        an object containing response code and JSON.
        '''
        url = self.get_handler_url(function, block_urlname)
        resp = self.client.post(url, json.dumps(data), '')
        ajax_response = namedtuple('AjaxResponse',
                                   ['data', 'status_code'])
        ajax_response.data = json.loads(resp.content)
        ajax_response.status_code = resp.status_code
        return resp

    def render_block(self, block_urlname):
        '''
        Return a rendering of the XBlock.

        We should include data, but with a selector dropping
        the rest of the HTML around the block.

        TODO: IMPLEMENT.
        '''
        section = self._containing_section(block_urlname)
        html_response = namedtuple('HtmlResponse',
                                   ['status_code'])
        #html_response.status_code = 200
        #return html_response

        url = self.urls[section]
        print url
        response = self.client.get(url)
        http_response.status_code = response.status_code
        return html_response

    def select_student(self, user_number):
        '''
        Select a new user. By default, we're populated with two normal
        users and one staff.

        This is not finished. I'm not sure the best way to do
        this. We'd like some kind of nicer parameter than a
        number. Ideally, we'd take something semantically named
        (student_0, staff_1, etc.) but iterable (for student in
        students:).
        '''
        email = self.STUDENTS[user_number][0]
        password = self.STUDENTS[user_number][1]
        print email
        print password
        self.login(email, password)
