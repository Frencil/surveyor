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
        assert 'stub index' in str(rv.data)


    def test_create_unopened_survey(self):
        s1 = surveyor.Survey('test unopened', 'test text')
        surveyor.db.session.add(s1)
        surveyor.db.session.commit()
        survey = surveyor.Survey.query.filter_by(title='test unopened').first()
        assert survey.title == 'test unopened'
        assert survey.is_open == 0
        assert survey.date_created is not None
        assert survey.date_opened is None
        assert survey.date_closed is None

    def test_create_opened_survey(self):
        s1 = surveyor.Survey('test opened', 'test text', True)
        surveyor.db.session.add(s1)
        surveyor.db.session.commit()
        survey = surveyor.Survey.query.filter_by(title='test opened').first()
        assert survey.title == 'test opened'
        assert survey.is_open == 1
        assert survey.date_created is not None
        assert survey.date_opened is not None
        assert survey.date_closed is None
        assert survey.date_opened > survey.date_created

    def test_create_survey_with_questions(self):
        s1 = surveyor.Survey('test with questions', 'test text')
        q1 = surveyor.Question('test text 1', s1)
        q2 = surveyor.Question('test text 2', s1)
        surveyor.db.session.add(s1)
        surveyor.db.session.add(q1)
        surveyor.db.session.add(q2)
        surveyor.db.session.commit()
        survey = surveyor.Survey.query.filter_by(title='test with questions').first()
        assert survey.title == 'test with questions'
        assert survey.is_open == 0
        

if __name__ == '__main__':
    unittest.main()
