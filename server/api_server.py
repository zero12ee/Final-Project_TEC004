# ==========================================
# Author: Pham Gia Bao (Student ID: AUS15065)
# Project ID: TEC004/05
# Description: Flask API Server for React Frontend
# ==========================================

# Import Flask core classes and functions:
# - Flask: creates the web application instance.
# - request: provides access to incoming HTTP request data.
# - jsonify: converts Python dictionaries into JSON responses.
from flask import Flask, request, jsonify

# Import CORS middleware so the React client can call this API from a different origin.
from flask_cors import CORS

import json

# Import password hashing utilities.
# - generate_password_hash: safely hash plain text passwords before storage.
# - check_password_hash: verify a plain text password against a stored hash.
from werkzeug.security import generate_password_hash, check_password_hash

# Import the Database wrapper that manages SQLite storage.
from database import Database
from data_manager import DataManager

# Initialize the Flask application.
app = Flask(__name__)

# Enable CORS for all routes and origins.
# This allows the React frontend to make requests to this Flask API from localhost or another domain.
CORS(app)

# Initialize the database helper instance.
# The Database class encapsulates user and course CRUD operations.
db = Database()
# Initialize CSV import/export helper.
data_manager = DataManager()


# -----------------------------
# Authentication endpoints
# -----------------------------

@app.route('/api/signup', methods=['POST'])
def signup():
    """
    Handle user sign-up requests.

    Expected request body:
      {
        "id": "studentId",
        "email": "student@example.com",
        "password": "plainTextPassword"
      }

    Returns JSON with the created user information on success.
    """

    # Read the JSON body from the incoming request.
    # If there is no JSON payload, use an empty dictionary to avoid exceptions.
    data = request.json or {}

    # Extract the expected fields from the request JSON.
    username = data.get('id')
    email = data.get('email')
    password = data.get('password')

    # Validate that all required signup fields are present.
    if not username or not email or not password:
        return jsonify({'error': 'Missing username, email, or password.'}), 400

    # Prevent duplicate username registration.
    if db.get_user_by_username(username):
        return jsonify({'error': 'Username already exists.'}), 400

    # Save the new user in the database.
    # The database helper will hash the password internally before storage.
    user_id = db.create_user(username, email, password)

    # Return the new user data, but never expose the password hash.
    return jsonify({
        'status': 'success',
        'user': {
            'id': user_id,
            'username': username,
            'email': email,
        },
    })


@app.route('/api/auth', methods=['POST'])
def auth():
    """
    Handle user authentication requests.

    Expected request body:
      {
        "id": "studentId",
        "password": "plainTextPassword"
      }

    Returns the authenticated user data when credentials are valid.
    """

    data = request.json or {}
    username = data.get('id')
    password = data.get('password')

    if not username or not password:
        return jsonify({'error': 'Missing username or password.'}), 400

    # Retrieve the stored user record by username.
    user = db.get_user_by_username(username)

    # Verify that the user exists and the password is correct.
    if not user or not check_password_hash(user['password_hash'], password):
        return jsonify({'error': 'Invalid credentials.'}), 401

    # Return authenticated user info without sending the password hash.
    return jsonify({
        'status': 'success',
        'user': {
            'id': user['id'],
            'username': user['username'],
            'email': user['email'],
        },
    })


# -----------------------------
# Course management endpoints
# -----------------------------

@app.route('/api/courses', methods=['GET', 'POST'])
def courses():
    """
    Supports two operations on the same endpoint:
      - GET: fetch all courses for a specific user.
      - POST: create a new course for a user.
    """

    if request.method == 'GET':
        # GET /api/courses?user_id=<id>
        # The frontend should supply the user_id query parameter.
        user_id = request.args.get('user_id')
        if not user_id:
            return jsonify({'error': 'Missing user_id query parameter.'}), 400

        # Fetch all courses belonging to the requested user.
        courses = db.get_courses_for_user(int(user_id))
        return jsonify({'courses': courses})

    # POST /api/courses
    # Create a new course document in the database.
    data = request.json or {}
    user_id = data.get('user_id')
    name = data.get('name')
    components = data.get('components')

    # Optional grading configuration fields with defaults.
    expected_total = data.get('expectedTotal', 100.0)
    passing_threshold = data.get('passingThreshold', 60.0)

    # Validate required course payload fields.
    if not user_id or not name or not isinstance(components, list):
        return jsonify({'error': 'Missing course data.'}), 400

    # Save the course and its components to the database.
    course_id = db.create_course(
        int(user_id),
        name,
        components,
        expected_total,
        passing_threshold,
    )

    # Return the created course details back to the client.
    course = {
        'id': course_id,
        'name': name,
        'components': components,
        'expectedTotal': expected_total,
        'passingThreshold': passing_threshold,
    }
    return jsonify({'status': 'created', 'course': course})


@app.route('/api/import-subject-scores', methods=['POST'])
def import_subject_scores():
    csv_file = request.files.get('csv_file')
    user_id = request.form.get('user_id')
    expected_totals = request.form.get('expectedTotals')
    default_expected_total = float(request.form.get('defaultExpectedTotal', 100.0))
    output_path = request.form.get('output_path')

    if not csv_file:
        return jsonify({'error': 'Missing csv_file upload.'}), 400

    try:
        expected_totals = json.loads(expected_totals) if expected_totals else {}
    except Exception:
        expected_totals = {}

    try:
        result = data_manager.import_subject_scores_from_file(
            csv_file,
            expected_totals,
            default_expected_total,
        )
    except Exception as e:
        return jsonify({'error': f'Failed to import CSV: {e}'}), 500

    created_courses = []
    if user_id:
        try:
            user_id_int = int(user_id)
            for subject in result.get('subjects', []):
                subject_name = subject.get('subject') or 'Imported Course'
                student_ids = subject.get('studentIds', [])
                
                # Create a display name with student ID information
                if student_ids and len(student_ids) > 0:
                    student_id_str = ', '.join(student_ids)
                    display_name = f"{subject_name}\n(Student ID: {student_id_str})"
                else:
                    display_name = subject_name
                
                components = [
                    {
                        'name': comp.get('name', f'Component {index + 1}'),
                        'weight': comp.get('weight', 0) or 0,
                        'maxPoints': comp.get('maxPoints', 100) or 100,
                        'score': comp.get('score'),
                    }
                    for index, comp in enumerate(subject.get('components', []))
                ]

                if not components:
                    continue

                course_id = db.create_course(
                    user_id_int,
                    display_name,  # Use display name with student ID
                    components,
                    subject.get('expectedTotal', default_expected_total),
                    60,
                )
                # Fetch the course back from database to get component IDs
                created_course = db.get_course(course_id, user_id_int)
                if created_course:
                    created_courses.append({
                        'id': course_id,
                        'name': display_name,
                        'components': created_course.get('components', components),
                        'expectedTotal': subject.get('expectedTotal', default_expected_total),
                        'passingThreshold': 60,
                        'studentIds': student_ids,  # Include student IDs in response
                    })
        except ValueError:
            created_courses = []

    if output_path:
        try:
            data_manager.export_to_json(result, output_path)
        except Exception as e:
            return jsonify({'error': f'Failed to export JSON: {e}'}), 500

    response_body = {'parsed': result}
    if created_courses:
        response_body['createdCourses'] = created_courses
    return jsonify(response_body)


@app.route('/api/courses/<int:course_id>', methods=['PUT'])
def update_course(course_id):
    """
    Update an existing course record by its numeric course_id.

    Expected request body contains the user_id for authorization,
    updated course name, component list, and grading configuration.
    """

    data = request.json or {}
    user_id = data.get('user_id')
    name = data.get('name')
    components = data.get('components')
    expected_total = data.get('expectedTotal', 100.0)
    passing_threshold = data.get('passingThreshold', 60.0)

    if not user_id or not name or not isinstance(components, list):
        return jsonify({'error': 'Missing course data.'}), 400

    # Update the matching course record in the database.
    updated = db.update_course(
        course_id,
        int(user_id),
        name,
        components,
        expected_total,
        passing_threshold,
    )

    if not updated:
        return jsonify({'error': 'Course not found or unauthorized.'}), 404

    course = {
        'id': course_id,
        'name': name,
        'components': components,
        'expectedTotal': expected_total,
        'passingThreshold': passing_threshold,
    }
    return jsonify({'status': 'updated', 'course': course})


# -----------------------------
# Prediction endpoint
# -----------------------------

@app.route('/api/predict', methods=['POST'])
def predict_grade():
    """
    Predict the current grade percentage and the score needed on remaining components.

    The request body should include the course components, each with:
      - max_points
      - weight
      - input_points (optional if not yet entered)
      - passingThreshold (optional threshold to compare against)

    The response includes the current percentage, required score, and pass/fail status.
    """

    data = request.json or {}
    components = data.get('components', [])
    target_percentage = data.get('passingThreshold', 60.0)

    total_secured = 0
    remaining_weight = 0

    for comp in components:
        # If the component has a score entered, convert it to a number.
        if comp.get('input_points') is not None and comp.get('input_points') != "":
            pts = float(comp['input_points'])
            # Normalize the entered points to the component's weight value.
            total_secured += (pts / comp['max_points']) * comp['weight']
        else:
            # For components without a score, accumulate the remaining weight.
            remaining_weight += comp['weight']

    # Determine how much of the target threshold is still required.
    needed = target_percentage - total_secured

    # If there is remaining weight, compute the average percentage needed.
    predicted_avg_needed = (needed / remaining_weight) * 100 if remaining_weight > 0 else 0

    return jsonify({
        'current_total': round(total_secured, 2),
        'suggested_score_needed': round(predicted_avg_needed, 2),
        'is_passing': total_secured >= target_percentage,
    })


# When this file is executed directly, start the Flask development server.
# Debug mode is enabled so errors are shown in the browser and the server reloads on code changes.
if __name__ == '__main__':
    app.run(debug=True, port=5000)
