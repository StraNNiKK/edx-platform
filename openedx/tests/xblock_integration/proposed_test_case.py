'''
This is a simple XBlock test case.
'''

from xblock_testcase import XBlockTestCase

olx = [
    """<vertical>
          <done url_name="done0"/>
          <done url_name="done1"/>
    </vertical>"""
]


class TestDone(XBlockTestCase):
    test_configuration = [
        {
            "olx": olx,
            "xblocks": [  # Stopgap until we handle OLX
                {
                    'blocktype': 'done',
                    'block_id': 'done0'
                },
                {
                    'blocktype': 'done',
                    'block_id': 'done1'
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

    def check_response(xblock_id, rendering):
        response = self.render_response()
        self.assertEqual(response.status, 200)
        self.assertScreenshot(xblock_id, rendering)

    def test_done(self):
        self.select_student(self.students[0])
        # We confirm we don't have errors rendering the student view
        self.check_response('done0', 'done-unmarked')
        self.check_response('done1', 'done-unmarked')
        # We confirm the block is initially false
        self.check_ajax(0, {}, False)
        self.check_ajax(1, {}, False)
        # We confirm we can toggle state both ways
        self.check_ajax(0, {'done': True}, True)
        self.check_ajax(1, {'done': False}, False)
        self.check_ajax(0, {'done': False}, False)
        self.check_ajax(1, {'done': True}, True)
        # We confirm state sticks around
        self.check_ajax(0, {}, False)
        self.check_ajax(1, {}, True)
        self.check_response('done0', 'done-unmarked')
        self.check_response('done1', 'done-marked')
        # We reconfirm we don't have errors rendering the student view
        self.assert_request_status_code(200, self.course_url)
        self.assert_screenshot('true-rendering')
