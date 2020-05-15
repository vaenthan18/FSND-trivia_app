import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgresql://{}/{}".format('localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        self.new_question = Question(
            question = 'What is the diameter of the Earth?',
            answer = '12,742 km',
            category ='1',
            difficulty = 5
        )

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
    
    def tearDown(self):
        """Executed after reach test"""
        pass

    def test_get_categories(self):
        res = self.client().get('/categories')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(len(data['categories']))

    def test_get_questions(self):
        res = self.client().get('/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['currentCategory'], None)
        self.assertTrue(len(data['categories']))
        self.assertTrue(len(data['questions']))

    def test_404_questions_page_dne(self):
        res = self.client().get('/questions?page=1000')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')

    def test_delete_question(self):
        newQuestion = self.new_question
        newQuestion.insert()
        res = self.client().delete('/questions/{}'.format(newQuestion.id))
        data = json.loads(res.data)
        question = Question.query.filter(Question.id == newQuestion.id).one_or_none()

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(question, None)
        self.assertEqual(data['deleted'], newQuestion.id)
        self.assertTrue(len(data['questions']))

    def test_422_deleting_question_dne(self):
        res = self.client().delete('/questions/123123')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'unprocessable')
    
    def test_new_question(self):
        res = self.client().post('/questions', json=self.new_question.format())
        data = json.loads(res.data)

        self.assertEqual(data['success'], True)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['created'])
        self.assertTrue(len(data['questions']))
    
    def test_400_new_question_json_bad_format(self):
        res = self.client().post('/questions', json={'difficulty': 'blah'})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 400)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'bad request')

    def test_search_question(self):
        res = self.client().post('/searchQuestions', json={'searchTerm': 'the'})
        data = json.loads(res.data)

        self.assertEqual(data['success'], True)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(len(data['questions']))

    def test_questions_by_category(self):
        res = self.client().get('/categories/1/questions')
        data = json.loads(res.data)

        self.assertEqual(data['success'], True)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(len(data['questions']))
        self.assertTrue(data['total_questions'])
        self.assertEqual(data['currentCategory'], 1)

    def test_404_questions_by_categories_category_dne(self):
        res = self.client().get('/categories/1000/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')
    
    def test_get_quiz(self):
        res = self.client().post('/quizzes', json={
            'previous_questions': [13, 4],
            'quiz_category': {
                'id':2
            }
        })
        data = json.loads(res.data)

        self.assertEqual(data['success'], True)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['question']['id'] in data['previousQuestions'])
        self.assertTrue(data['question'])

    def test_400_quiz_json_bad_format(self):
        res = self.client().post('/quizzes', json={
            'previous_questions': [],
            'quiz_category': {
                'id':'break'
            }
        })
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 400)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'bad request')


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()