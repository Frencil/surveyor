# -*- coding: utf-8 -*-

import os
import surveyor
import unittest
import tempfile

class SurveyorTestCase(unittest.TestCase):

    def setUp(self):
        self.db_fd, surveyor.app.config['DATABASE'] = tempfile.mkstemp()
        surveyor.app.config['TESTING'] = True
        self.app = surveyor.app.test_client()
        surveyor.init_db()

    def tearDown(self):
        os.close(self.db_fd)
        os.unlink(surveyor.app.config['DATABASE'])

    def test_empty_db(self):
        rv = self.app.get('/')
        assert 'No surveys here so far' in str(rv.data)

    '''
    def test_messages(self):
        self.login('admin', 'default')
        rv = self.app.post('/add', data=dict(
            title='<Hello>',
            text='<strong>HTML</strong> allowed here'
        ), follow_redirects=True)
        assert 'No entries here so far' not in rv.data
        assert '&lt;Hello&gt;' in rv.data
        assert '<strong>HTML</strong> allowed here' in rv.data
    '''

if __name__ == '__main__':
    unittest.main()
