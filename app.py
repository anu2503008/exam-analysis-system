# app.py
from flask import Flask, render_template, request, redirect, url_for, jsonify
import os
import json
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'exam-analysis-secret-key'

# Data storage (in-memory for simplicity)
STUDENTS_FILE = 'students_data.json'

def load_students():
    """Load students data from JSON file"""
    if os.path.exists(STUDENTS_FILE):
        try:
            with open(STUDENTS_FILE, 'r') as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_students(students):
    """Save students data to JSON file"""
    with open(STUDENTS_FILE, 'w') as f:
        json.dump(students, f, indent=2)

# Sample initial data
INITIAL_STUDENTS = {
    "101": {
        "roll_no": "101",
        "name": "Student A",
        "class": "10",
        "school": "XYZ High School",
        "photo": "https://via.placeholder.com/100?text=Student+A",
        "subjects": {
            "Math": {"marks": 40, "percentage": 40, "grade": "C"},
            "Science": {"marks": 75, "percentage": 75, "grade": "B"},
            "English": {"marks": 85, "percentage": 85, "grade": "A"}
        },
        "attendance": 65,
        "quiz_scores": {"Math": 4, "Science": 7, "English": 8},
        "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
}

@app.route('/')
def index():
    """Home page - Student list"""
    students = load_students()
    if not students:
        save_students(INITIAL_STUDENTS)
        students = INITIAL_STUDENTS
    return render_template('index.html', students=students)

@app.route('/student/<roll_no>')
def student_report(roll_no):
    """View individual student report"""
    students = load_students()
    if roll_no not in students:
        return redirect(url_for('index'))
    
    student = students[roll_no]
    
    # Calculate additional insights
    insights = []
    suggestions = []
    
    # Subject analysis
    weak_subjects = []
    strong_subjects = []
    for subject, data in student['subjects'].items():
        if data['percentage'] < 50:
            weak_subjects.append(subject)
            insights.append(f"Weak in {subject} (marks: {data['marks']}%)")
            suggestions.append(f"{subject}: Practice basics daily. Focus on fundamental concepts.")
        elif data['percentage'] >= 75:
            strong_subjects.append(subject)
            insights.append(f"Strong in {subject} (marks: {data['marks']}%)")
    
    # Quiz analysis
    quiz_insights = []
    for subject, score in student['quiz_scores'].items():
        quiz_percent = (score / 10) * 100
        if quiz_percent < 50:
            quiz_insights.append(f"Quiz performance weak in {subject}: {score}/10")
        elif quiz_percent >= 70:
            quiz_insights.append(f"Good quiz performance in {subject}: {score}/10")
    
    if quiz_insights:
        insights.extend(quiz_insights)
        suggestions.append("Quiz: Focus on weak topics and practice more questions.")
    
    # Attendance analysis
    attendance = student['attendance']
    if attendance < 75:
        insights.append(f"Low attendance: {attendance}% (below 75%)")
        suggestions.append(f"Attendance: Improve to 80%+. Consider discussing attendance concerns.")
    elif attendance < 85:
        insights.append(f"Fair attendance: {attendance}%")
    else:
        insights.append(f"Good attendance: {attendance}%")
        suggestions.append("Attendance: Maintain current attendance record.")
    
    # Overall performance
    avg_percentage = sum(d['percentage'] for d in student['subjects'].values()) / len(student['subjects'])
    if avg_percentage < 50:
        insights.append(f"Academic performance needs significant improvement")
        suggestions.append("Consider additional tutoring and create a structured study plan.")
    elif avg_percentage < 70:
        insights.append(f"Academic performance is satisfactory but has room for improvement")
        suggestions.append("Focus on weak subjects while maintaining strong ones.")
    else:
        insights.append(f"Good academic performance")
        suggestions.append("Keep up the good work! Challenge yourself with advanced topics.")
    
    # Ensure we have enough insights/suggestions
    if len(insights) < 3:
        insights.append("Regular revision is recommended for all subjects")
        suggestions.append("Create a weekly revision schedule.")
    
    if len(suggestions) < 3:
        suggestions.append("Consider group study sessions for better understanding.")
        suggestions.append("Use online resources for additional practice.")
    
    return render_template('report.html', student=student, insights=insights[:5], suggestions=suggestions[:5], quiz_scores=student['quiz_scores'])

@app.route('/add_student', methods=['GET', 'POST'])
def add_student():
    """Add a new student"""
    if request.method == 'POST':
        students = load_students()
        
        roll_no = request.form['roll_no']
        if roll_no in students:
            return render_template('add_student.html', error="Roll number already exists!")
        
        new_student = {
            "roll_no": roll_no,
            "name": request.form['name'],
            "class": request.form['class'],
            "school": request.form['school'],
            "photo": request.form.get('photo', f"https://via.placeholder.com/100?text={request.form['name'][:2]}"),
            "subjects": {
                "Math": {"marks": int(request.form['math_marks']), "percentage": int(request.form['math_marks']), "grade": calculate_grade(int(request.form['math_marks']))},
                "Science": {"marks": int(request.form['science_marks']), "percentage": int(request.form['science_marks']), "grade": calculate_grade(int(request.form['science_marks']))},
                "English": {"marks": int(request.form['english_marks']), "percentage": int(request.form['english_marks']), "grade": calculate_grade(int(request.form['english_marks']))}
            },
            "attendance": int(request.form['attendance']),
            "quiz_scores": {
                "Math": int(request.form['math_quiz']),
                "Science": int(request.form['science_quiz']),
                "English": int(request.form['english_quiz'])
            },
            "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        students[roll_no] = new_student
        save_students(students)
        return redirect(url_for('index'))
    
    return render_template('add_student.html', error=None)

def calculate_grade(marks):
    """Calculate grade based on marks"""
    if marks >= 90:
        return "A+"
    elif marks >= 80:
        return "A"
    elif marks >= 70:
        return "B"
    elif marks >= 60:
        return "C"
    elif marks >= 50:
        return "D"
    else:
        return "F"

@app.route('/delete_student/<roll_no>')
def delete_student(roll_no):
    """Delete a student record"""
    students = load_students()
    if roll_no in students:
        del students[roll_no]
        save_students(students)
    return redirect(url_for('index'))

@app.route('/analytics')
def analytics():
    """Overall analytics dashboard"""
    students = load_students()
    
    if not students:
        return render_template('analytics.html', stats={})
    
    # Calculate overall statistics
    total_students = len(students)
    avg_attendance = sum(s['attendance'] for s in students.values()) / total_students
    avg_math = sum(s['subjects']['Math']['marks'] for s in students.values()) / total_students
    avg_science = sum(s['subjects']['Science']['marks'] for s in students.values()) / total_students
    avg_english = sum(s['subjects']['English']['marks'] for s in students.values()) / total_students
    
    # Grade distribution
    grade_dist = {"A+": 0, "A": 0, "B": 0, "C": 0, "D": 0, "F": 0}
    for student in students.values():
        for subject in student['subjects'].values():
            grade_dist[subject['grade']] += 1
    
    # Top performers (by average percentage)
    performers = []
    for roll, student in students.items():
        avg_perc = sum(s['percentage'] for s in student['subjects'].values()) / 3
        performers.append({
            "name": student['name'],
            "roll_no": roll,
            "avg_percentage": avg_perc
        })
    performers.sort(key=lambda x: x['avg_percentage'], reverse=True)
    
    stats = {
        "total_students": total_students,
        "avg_attendance": round(avg_attendance, 1),
        "avg_math": round(avg_math, 1),
        "avg_science": round(avg_science, 1),
        "avg_english": round(avg_english, 1),
        "grade_distribution": grade_dist,
        "top_performers": performers[:5]
    }
    
    return render_template('analytics.html', stats=stats)

@app.route('/update_quiz', methods=['POST'])
def update_quiz():
    """Update quiz scores via AJAX"""
    data = request.get_json()
    roll_no = data.get('roll_no')
    subject = data.get('subject')
    new_score = int(data.get('score'))
    
    students = load_students()
    if roll_no in students and subject in students[roll_no]['quiz_scores']:
        students[roll_no]['quiz_scores'][subject] = new_score
        students[roll_no]['last_updated'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        save_students(students)
        return jsonify({"success": True, "message": "Quiz score updated!"})
    
    return jsonify({"success": False, "message": "Update failed"})

if __name__ == '__main__':
    app.run(debug=True)