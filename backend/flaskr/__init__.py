from crypt import methods
from nis import cat
import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import and_
from flask_cors import CORS, cross_origin
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)
    CORS(app)

    CORS(app, resources={r"/api/*": {"origins": "*"}})

    # CORS Headers 
    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,true')
        response.headers.add('Access-Control-Allow-Methods', 'GET,PATCH,POST,DELETE,OPTIONS')
        return response

    """
    @TODO:
    Create an endpoint to handle GET requests
    for all available categories.
    """
    @app.route("/categories")
    @cross_origin()
    def get_categories():
        categories = Category.query.all()
       
        return jsonify({
            'success': True,
            'categories': [category for category in categories]
        })

    @app.route('/questions')
    @cross_origin()
    def get_questions():
        page = request.args.get('page', 1, type=int)
        start = (page - 1) * QUESTIONS_PER_PAGE
        end = start + QUESTIONS_PER_PAGE

        questions = Question.query.all()
        
        return jsonify({
            'success': True,
            'questions':[question for question in questions[start:end]],
            'total_questions':len(questions)
        })
    """
    @TODO:
    Create an endpoint to handle GET requests for questions,
    including pagination (every 10 questions).
    This endpoint should return a list of questions,
    number of total questions, current category, categories.

    TEST: At this point, when you start the application
    you should see questions and categories generated,
    ten questions per page and pagination at the bottom of the screen for three pages.
    Clicking on the page numbers should update the questions.
    """

    @app.route('/questions/<id>', methods=['DELETE'])
    @cross_origin()
    def delete_question(id):
        Question.query.fetch(id).delete()
        return jsonify({'success': True})

    """
    @TODO:
    Create an endpoint to DELETE question using a question ID.

    TEST: When you click the trash icon next to a question, the question will be removed.
    This removal will persist in the database and when you refresh the page.
    """

    @app.route('/questions', methods=['POST'])
    @cross_origin()
    def create_question():
        question = Question(
            question=request.form.get('question'),
            answer=request.form.get('answer'),
            category=request.form.get('category'),
            difficulty=request.form.get('difficulty')
        ).insert()
        return jsonify({'success': True, 'question': question.id})

    """
    @TODO:
    Create an endpoint to POST a new question,
    which will require the question and answer text,
    category, and difficulty score.

    TEST: When you submit a question on the "Add" tab,
    the form will clear and the question will appear at the end of the last page
    of the questions list in the "List" tab.
    """

    @app.route('/questions/search', methods=['POST'])
    @cross_origin()
    def search_questions():
        search_term = request.form.get('searchTerm', '')
        current_category = request.form.get('currentCategory')
        search = "%{}%".format(search_term)
        questions = Question.query.filter(and_(Question.question.ilike(search), Question.category==current_category)).all()
        return jsonify({
            'success': True,
            'questions': [Question.format() for question in questions],
            'current_category': current_category
        })
    """
    @TODO:
    Create a POST endpoint to get questions based on a search term.
    It should return any questions for whom the search term
    is a substring of the question.

    TEST: Search by any phrase. The questions list will update to include
    only question that include that string within their question.
    Try using the word "title" to start.
    """

    @app.route('/categories/<category>/questions')
    @cross_origin()
    def get_questions_by_category(category):
        questions = Question.query.filter(Question.category == category).all()

        return jsonify({
            'success': True,
            'questions': [question.format() for question in questions],
            'current_category': category
        })

    """
    @TODO:
    Create a GET endpoint to get questions based on category.

    TEST: In the "List" tab / main screen, clicking on one of the
    categories in the left column will cause only questions of that
    category to be shown.
    """

    @app.route('questions/play', methods=['POST'])
    @cross_origin()
    def fresh_question():
        category = request.form.get('category')
        previous_questions = request.form.get('previous_questions')

        other_possibilities = Question.query.filter(and_(Question.category==category, id not in previous_questions))
        return jsonify({
            'success': True,
            'question': other_possibilities.first().format()
        })


    """
    @TODO:
    Create a POST endpoint to get questions to play the quiz.
    This endpoint should take category and previous question parameters
    and return a random questions within the given category,
    if provided, and that is not one of the previous questions.

    TEST: In the "Play" tab, after a user selects "All" or a category,
    one question at a time is displayed, the user is allowed to answer
    and shown whether they were correct or not.
    """

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "success": False, 
            "error": 404,
            "message": "Not found"
        }), 404

    @app.errorhandler(422)
    def unproccessable_entity(error):
        return jsonify({
            "success": False, 
            "error": 422,
            "message": "Unprocessable entity"
        }), 422

    return app

