import os
import select
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def paginate_questions(request, selection):
    page = request.args.get("page", 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE

    questions = [question.format() for question in selection]
    current_books = questions[start:end]

    return current_books

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)

    """
    DONE: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
    """
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    """
    DONE: Use the after_request decorator to set Access-Control-Allow
    """
    # CORS Headers
    @app.after_request
    def after_request(response):
        response.headers.add(
            "Access-Control-Allow-Headers", "Content-Type,Authorization,true"
        )
        response.headers.add(
            "Access-Control-Allow-Methods", "GET,PUT,POST,DELETE,OPTIONS"
        )
        return response

    """
    DONE:
    Create an endpoint to handle GET requests
    for all available categories.

    """
    @app.route("/categories")
    def retrieve_cate():
        category = Category.query.order_by(Category.id).all()
        
        obj_catetegory = {}
        
        for i in category:
            obj_catetegory[str(i.id)] = i.type        

        return jsonify(
            {
                'success':True,
                "categories": obj_catetegory
            }
        )

    # @app.route('/')
    # def hello_world():
    #     return 'Hello, World!'

    """
    DONE:
    Create an endpoint to handle GET requests for questions,
    including pagination (every 10 questions).
    This endpoint should return a list of questions,
    number of total questions, current category, categories.


    DONE: At this point, when you start the application
    you should see questions and categories generated,
    ten questions per page and pagination at the bottom of the screen for three pages.
    Clicking on the page numbers should update the questions.
    """
    @app.route('/questions')
    def retrieve_questions():
        cateory_selection = random.randint(1, 6)
        selection = Question.query.filter_by(category=cateory_selection).order_by(Question.id).all()
        current_questions = paginate_questions(request, selection)
        category = Category.query.order_by(Category.id).all()
        
        obj_catetegory = {}
        
        for i in category:
            obj_catetegory[str(i.id)] = i.type

        

        if len(current_questions) == 0:
            abort(404)
        
        return jsonify({
            'success': True,
            'questions':current_questions,
            'totalQuestions':len(selection),
            'categories': obj_catetegory,
            "currentCategory": obj_catetegory[str(cateory_selection)]
        })

    """
    DONE:
    Create an endpoint to DELETE question using a question ID.

    DONE: When you click the trash icon next to a question, the question will be removed.
    This removal will persist in the database and when you refresh the page.
    """

    @app.route("/questions/<int:question_id>", methods=["DELETE"])
    def delete_question(question_id):
        try:
            question = Question.query.filter(Question.id == question_id).one_or_none()

            if question is None:
                abort(404)

            question.delete()
            selection = Question.query.order_by(Question.id).all()
            current_questions = paginate_questions(request, selection)

            return jsonify(
                {
                    "success": True,
                    "deleted": question_id,                
                }
            )

        except:
            abort(422)

    """
    @DONE:
    Create an endpoint to POST a new question,
    which will require the question and answer text,
    category, and difficulty score.

    DONE: When you submit a question on the "Add" tab,
    the form will clear and the question will appear at the end of the last page
    of the questions list in the "List" tab.
    """

    @app.route("/questions", methods=["POST"])
    def create_question():
        body = request.get_json()

        new_question = body.get("question", None)
        new_answer = body.get("answer", None)
        new_category = body.get("category", None)
        new_difficulty = body.get("difficulty", None)
        search = body.get("searchTerm", None)

        try:
            if search:
                selection = Question.query.order_by(Question.id).filter(
                    Question.question.ilike("%{}%".format(search))
                )
                
                current_questions = paginate_questions(request, selection)

                return jsonify(
                    {
                        "success": True,
                        "questions": current_questions,
                        "totalQuestions": len(selection.all()),
                        "currentCategory": "Entertainment"
                    }
                )
            else:
                question = Question(question=new_question, answer=new_answer, category=new_category, difficulty=new_difficulty)
                question.insert()

                selection = Question.query.order_by(Question.id).all()
                current_questions = paginate_questions(request, selection)

                return jsonify(
                    {
                        "success": True
                        
                    }
                )

        except:
            abort(422)

    """
    DONE:
    Create a POST endpoint to get questions based on a search term.
    It should return any questions for whom the search term
    is a substring of the question.

    DONE: Search by any phrase. The questions list will update to include
    only question that include that string within their question.
    Try using the word "title" to start.
    """

    """
    @DONE:
    Create a GET endpoint to get questions based on category.

    DONE: In the "List" tab / main screen, clicking on one of the
    categories in the left column will cause only questions of that
    category to be shown.
    """
    @app.route('/categories/<int:category_id>/questions')
    def retrieve_questions_by_category(category_id):
        seletion = Question.query.filter_by(category=category_id).all()
        current_questions = paginate_questions(request, seletion)

        if len(current_questions) == 0:
            abort(404)
        
        return jsonify({
            'success': True,
            'questions':current_questions,
            'totalQuestions':len(seletion)
        })

    """
    DONE:
    Create a POST endpoint to get questions to play the quiz.
    This endpoint should take category and previous question parameters
    and return a random questions within the given category,
    if provided, and that is not one of the previous questions.

    DONE: In the "Play" tab, after a user selects "All" or a category,
    one question at a time is displayed, the user is allowed to answer
    and shown whether they were correct or not.
    """

    @app.route("/quizzes", methods=["POST"])
    def quizzes():
        body = request.get_json()

        previous_questions = body.get("previous_questions", None)
        quiz_category = body.get("quiz_category", None)
        category_id = quiz_category['id']

        print(previous_questions)
        print(category_id)
        try:
            
            if category_id == 0:
                all_question = Question.query.all()
                all_id = []

                for i in all_question:
                    all_id.append(i.id)

                random_id = random.choice(all_id)

                while random_id in previous_questions:
                    random_id = random.choice(all_id)

                question = Question.query.filter(Question.id == random_id).one_or_none()

                return jsonify({
                        "question": question.format()
                        })
            else:
                all_question = Question.query.filter(Question.category == category_id).all()
                all_id = []

                for i in all_question:
                    all_id.append(i.id)

                random_id = random.choice(all_id)

                while random_id in previous_questions:
                    random_id = random.choice(all_id)

                question = Question.query.filter(Question.id == random_id).one_or_none()

                return jsonify({
                        "question": question.format()
                        })

        except:
            abort(422)
    """
    @DONE:
    Create error handlers for all expected errors
    including 404 and 422.    
    """
    @app.errorhandler(404)
    def not_found(error):
        return (
            jsonify({"success": False, "error": 404, "message": "resource not found"}),
            404,
        )

    @app.errorhandler(422)
    def unprocessable(error):
        return (
            jsonify({"success": False, "error": 422, "message": "unprocessable"}),
            422,
        )

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({"success": False, "error": 400, "message": "bad request"}), 400

    @app.errorhandler(405)
    def not_found(error):
        return (
            jsonify({"success": False, "error": 405, "message": "method not allowed"}),
            405,
        )



    return app

