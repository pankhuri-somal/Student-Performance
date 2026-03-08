# ---------- Total Marks Calculation ----------
def total_marks(internal, external):
    """
    Calculate total marks for a subject
    """
    if internal is None or external is None:
        return 0
    return internal + external


# ---------- Semester CGPA Calculation ----------
def calculate_sem_cgpa(subject_totals):
    """
    Calculate CGPA for one semester based on subject marks
    Also returns number of failed subjects (backlogs)
    """

    if not subject_totals:
        return 0, 0

    grade_points = []
    backlogs = 0

    for m in subject_totals:

        # Check subject fail
        if m < 40:
            backlogs += 1
            grade_points.append(0)

        elif m >= 90:
            grade_points.append(10)
        elif m >= 80:
            grade_points.append(9)
        elif m >= 70:
            grade_points.append(8)
        elif m >= 60:
            grade_points.append(7)
        elif m >= 50:
            grade_points.append(6)
        else:  # 40–49
            grade_points.append(5)

    cgpa = sum(grade_points) / len(grade_points)

    return round(cgpa, 2), backlogs


# ---------- Overall CGPA ----------
def overall_cgpa(sem_list):
    """
    Calculate overall CGPA from multiple semesters
    """

    if not sem_list:
        return 0

    return round(sum(sem_list) / len(sem_list), 2)


# ---------- Pass / Fail & Classification ----------
def pass_fail(cgpa, backlogs):
    """
    Determine pass/fail and classification
    """

    # If any backlog or CGPA below 5
    if cgpa < 5 or backlogs > 0:
        return "FAIL"

    elif 5.0 <= cgpa <= 5.9:
        return "PASS CLASS"

    elif 6.0 <= cgpa <= 6.9:
        return "SECOND CLASS"

    elif 7.0 <= cgpa <= 7.9:
        return "FIRST CLASS"

    elif cgpa >= 8.0:
        return "FIRST CLASS WITH DISTINCTION"