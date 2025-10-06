@app.route('/student/chat/<int:mentor_id>', methods=['GET', 'POST'])
def student_chat(mentor_id):
    student = get_logged_in_user()  # more reliable than current_user
    if not student or student.role != 'student':
        return redirect(url_for('login'))

    mentor = User.query.filter_by(id=mentor_id, role='mentor').first_or_404()

    if request.method == 'POST':
        message = request.form.get('message')
        if message:
            new_message = Message(
                content=message,
                student_id=student.id,
                mentor_id=mentor.id,
                sender_role='student'  # ✅ required
            )
            db.session.add(new_message)
            db.session.commit()
            return redirect(url_for('student_chat', mentor_id=mentor.id))

    messages = Message.query.filter_by(
        student_id=student.id, mentor_id=mentor.id
    ).order_by(Message.timestamp).all()

    return render_template('student_chat.html', student=student, mentor=mentor, messages=messages)
