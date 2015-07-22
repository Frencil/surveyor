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
        assert 'No questions here so far' in str(rv.data)

if __name__ == '__main__':
    unittest.main()
