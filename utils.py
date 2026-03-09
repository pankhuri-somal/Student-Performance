# ---------- CGPA & Prediction ---------- #

def calculate_cgpa(marks):
    grade_points = []
    for m in marks:
        if m >= 90:
            grade_points.append(10)
        elif m >= 80:
            grade_points.append(9)
        elif m >= 70:
            grade_points.append(8)
        elif m >= 60:
            grade_points.append(7)
        elif m >= 50:
            grade_points.append(6)
        elif m >= 40:
            grade_points.append(5)
        else:
            grade_points.append(0)
    return round(sum(grade_points)/len(grade_points), 2)

def predict_status(cgpa, backlogs, attendance):
    # Simple rule-based prediction
    if backlogs > 0 or cgpa < 5:
        return "FAIL"
    elif cgpa >= 5 and cgpa < 6:
        return "PASS CLASS"
    elif cgpa >= 6 and cgpa < 7:
        return "SECOND CLASS"
    elif cgpa >= 7 and cgpa < 8:
        return "FIRST CLASS"
    else:
        return "FIRST CLASS WITH DISTINCTION"