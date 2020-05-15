import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)

  # Setting up CORS for any origin and setting Access Control Headers
  CORS(app)

  @app.after_request
  def after_request(response):
    response.headers.add('Access-Control-Allow-Headers', 'Content-type, Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET, POST, DELETE, OPTIONS')
    return response


  # Paginate Questions given the page query argument from the request object and a list of questions
  def paginate_questions(request, questions):
    page = request.args.get('page', 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE
    formatted_questions = [question.format() for question in questions]
    return formatted_questions[start:end]

  # Get request for category dictionary with id keys and type values
  @app.route('/categories')
  def get_categories():
    categories = Category.query.order_by(Category.id).all()
    formatted_categories = {}
    for category in categories:
      formatted_categories[category.id] = category.type
    
    if (len(formatted_categories) == 0):
      abort(404)

    return jsonify({
      'success':True,
      'categories': formatted_categories
    })

  # Get request for a list of all questions - paginated
  @app.route('/questions')
  def get_questions():
    allQuestions = Question.query.order_by(Question.id).all()
    categories = Category.query.order_by(Category.id).all()
    formatted_categories = {}
    for category in categories:
      formatted_categories[category.id] = category.type
    
    questions = paginate_questions(request, allQuestions)

    if(len(questions) == 0):
      abort(404)

    return jsonify({
      'success': True,
      'questions': questions,
      'categories': formatted_categories,
      'currentCategory': None,
      'total_questions': len(allQuestions)
    })

  # Delete request for questions
  @app.route('/questions/<int:question_id>', methods=['DELETE'])
  def delete_question(question_id):
    try:
      del_question = Question.query.filter(Question.id == question_id).one_or_none()
      if del_question is None:
        abort(404)

      del_question.delete()
      questions = Question.query.order_by(Question.id).all()
      paginatedQuestions = paginate_questions(request, questions)
      return jsonify({
        'success': True,
        'deleted': question_id,
        'questions': paginatedQuestions
      })
    except:
      abort(422)

  # Post request to create new questions
  @app.route('/questions', methods=['POST'])
  def add_question():
    data = request.get_json()
    new_question = data.get('question', None)
    new_answer = data.get('answer', None)
    new_category = data.get('category', None)
    new_difficulty = data.get('difficulty', None)
    try:
      question = Question(question=new_question, answer=new_answer, category=new_category, difficulty=new_difficulty)
      question.insert()

      questions = Question.query.order_by(Question.id).all()
      paginatedQuestions = paginate_questions(request, questions)
      return jsonify({
        'success': True,
        'created': question.id,
        'questions': paginatedQuestions
      })
    except:
      abort(400)

  # Post request for searching questions based on a search term
  @app.route('/searchQuestions', methods=['POST'])
  def search_questions():
    data = request.get_json()
    search_term = data.get('searchTerm', None)
    try:
      filtered_books = Question.query.filter(Question.question.ilike('%{}%'.format(search_term))).all()
      paginatedQuestions = paginate_questions(request, filtered_books)
      return jsonify({
        'success': True,
        'questions': paginatedQuestions,
        'totalQuestions': len(filtered_books),
        'currentCategory': None
      })
    except:
      abort(422)

  # Get request for questions filtered by category
  @app.route('/categories/<int:category_id>/questions')
  def show_questions_by_catgory(category_id):
    questions = Question.query.filter(Question.category == category_id).order_by(Question.id).all()
    category = Category.query.get(category_id)
    paginatedQuestions = paginate_questions(request, questions)
    if(len(questions)==0):
      abort(404)
    return jsonify({
      'success':True,
      'questions': paginatedQuestions,
      'total_questions': len(questions),
      'currentCategory': category.format()['id']
    })

  # Post request for randomizes questions while playing
  @app.route('/quizzes', methods=['POST'])
  def get_quiz_questions():
    data = request.get_json()
    category = data.get('quiz_category', None)
    previous_questions = data.get('previous_questions', None)

    try:
      if (category['id'] == 0):
        questions = Question.query.filter(Question.id.notin_(previous_questions)).all()
      else:
        questions = Question.query.filter(Question.category == category['id']).filter(Question.id.notin_(previous_questions)).all()
      
      formatted_questions = [question.id for question in questions]
      next_question = random.choice(formatted_questions)
      previous_questions.append(next_question)
      return jsonify({
        'success': True,
        'question': Question.query.get(next_question).format(),
        'previousQuestions': previous_questions
      })
    except:
      abort(400)

  # Error Handlers
  @app.errorhandler(404)
  def not_found(error):
    return jsonify({
      'success': False,
      'error': 404,
      'message': 'resource not found'
    }), 404

  @app.errorhandler(422)
  def unprocessable(error):
    return jsonify({
      'success': False,
      'error': 422,
      'message': 'unprocessable'
    }), 422

  @app.errorhandler(400)
  def bad_request(error):
    return jsonify({
      'success': False,
      'error': 400,
      'message': 'bad request'
    }), 400
  
  return app

    