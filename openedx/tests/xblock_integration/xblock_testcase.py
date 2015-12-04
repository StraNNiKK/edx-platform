class XBlockTestCase(object):
    def setup(self):
        '''
        Unless overridden, we create two student users and one staff
        user. We create the course hierarchy based on the OLX defined
        in the XBlock.
        '''
        pass

    def assertScreenshot(self, block_id, rendering=None):
        '''
        As in Bok Choi, but instead of a CSS selector, we pass a
        block_id. We may want to be able to pass an optional selector
        for picking a subelement of the block.

        This confirms status code, and that the screenshot is
        identical.
        '''
        pass

    def ajax(self, function, block_id, json_data):
        '''
        Call a json_handler in the XBlock. Return the response as
        an object containing response code and JSON.
        '''
        pass

    def select_user(self, user, staff):
        '''
        Select a new user. By default, we're populated with two normal
        users and one staff.
        '''
        pass

    def select_page(self, page):
        '''
        If we define several pages, this lets us switch the current one
        '''
        pass
