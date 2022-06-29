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

        questions = [question for question in Question.query.all()[start:end]]
        categories = [question.category for question in questions]
        current_category = categories.first() if len(categories) > 0 else None
        return jsonify({
            'success': True,
            'questions': [question for question in questions[start:end]],
            'total_questions': len(questions),
            'categories': categories,
            'current_category': current_category
        })
   

    @app.route('/questions/<id>', methods=['DELETE'])
    @cross_origin()
    def delete_question(id):
        Question.query.fetch(id).delete()
        return jsonify({'success': True})


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

    @app.route('/questions/search', methods=['POST'])
    @cross_origin()
    def search_questions():
        search_term = request.form.get('searchTerm', '')
    
        search = "%{}%".format(search_term)
        questions = Question.query.filter(and_(Question.question.ilike(search), Question.category==current_category)).all()
        current_category = questions.first().category if len(questions) > 0 else None

        return jsonify({
            'success': True,
            'questions': [Question.format() for question in questions],
            'current_category': current_category
        })

    @app.route('/categories/<id>/questions')
    @cross_origin()
    def get_questions_by_category(id):
        category = Category.query.get(id).type
        questions = Question.query.filter(Question.category == category).all()
        return jsonify({
            'success': True,
            'total_questions': len(questions),
            'questions': [question.format() for question in questions],
            'current_category': category
        })


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

