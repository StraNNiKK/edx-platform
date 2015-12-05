'''
This is a simple XBlock test case.
'''
from xblock_testcase import XBlockTestCase

#from xmodule.modulestore.tests.django_utils import SharedModuleStoreTestCase as XBlockTestCase

olx = [
    """<vertical>
          <done urlname="done0"/>
          <done urlname="done1"/>
    </vertical>"""
]


class TestDone(XBlockTestCase):
    test_configuration = [
        {
            "urlname": "two_done_block_test",
            "olx": olx,
            "xblocks": [  # Stopgap until we handle OLX
                {
                    'blocktype': 'done',
                    'urlname': 'done0'
                },
                {
                    'blocktype': 'done',
                    'urlname': 'done1'
                }
            ]
        }
    ]

    def check_ajax(self, block, data, desired_state):
        """
        Make an AJAX call to the XBlock, and assert the state is as
        desired.
        """
        response = self.ajax('toggle_button', block, data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, {"state": desired_state})
        return response.data

    def check_response(self, block_urlname, rendering):
        response = self.render_block(block_urlname)
        self.assertEqual(response.status_code, 200)
        self.assertXBlockScreenshot(block_urlname, rendering)

    def test_done(self):
        #self.select_student(0)
        # We confirm we don't have errors rendering the student view
        self.check_response('done0', 'done-unmarked')
        self.check_response('done1', 'done-unmarked')
        # We confirm the block is initially false
        self.check_ajax('done0', {}, False)
        self.check_ajax('done1', {}, False)
        # We confirm we can toggle state both ways
        self.check_ajax('done0', {'done': True}, True)
        self.check_ajax('done1', {'done': False}, False)
        self.check_ajax('done0', {'done': False}, False)
        self.check_ajax('done1', {'done': True}, True)
        # We confirm state sticks around
        self.check_ajax('done0', {}, False)
        self.check_ajax('done1', {}, True)
        # Reconfirm no errors rendering pages, either by status code
        # or by screenshot
        self.check_response('done0', 'done-unmarked')
        self.check_response('done1', 'done-marked')
