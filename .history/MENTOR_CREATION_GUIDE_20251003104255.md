# Creating Mentor Users - Guide

## Method 1: Using the Setup Script (Quickest)

1. Open terminal in the project directory
2. Run: `python create_users.py`
3. This will create:
   - Admin user (admin@example.com / admin123)
   - 3 sample mentors (password: mentor123)
   - 1 sample student (student@example.com / student123)

## Method 2: Using Admin Dashboard (Manual)

### Step 1: Create Admin User (if needed)

If you don't have an admin user, you can modify the signup to temporarily create one:

1. Go to `/signup`
2. Fill the form
3. Temporarily change `role='student'` to `role='admin'` in the signup function (line 124 in app.py)
4. Sign up
5. Change it back to `role='student'`

### Step 2: Login and Create Mentors

1. Login with admin credentials
2. Go to `/admin_dashboard`
3. Scroll to "Add User" section
4. Fill the form:
   - **Name**: Mentor's full name
   - **Email**: Mentor's email address
   - **Password**: Temporary password for mentor
   - **Role**: Select "Mentor" from dropdown
5. Click "Add User"

## Method 3: Database Direct (Advanced)

If you have database access, you can insert directly:

```sql
INSERT INTO user (name, email, password, role, is_active)
VALUES ('Dr. John Doe', 'john.doe@example.com', 'hashed_password_here', 'mentor', 1);
```

## Verification

After creating mentor users:

1. Check admin dashboard - mentors should appear in the "All Users" list
2. Mentors should be available in assignment dropdowns
3. Mentors can login at `/login` with their credentials

## Default User Roles

- **admin**: Can manage users, assign mentors, view all chats
- **mentor**: Can view assigned students, chat with students
- **student**: Can upload projects, chat with assigned mentor

## Important Notes

- Mentors need to be assigned to students by admin
- Students can only chat with their assigned mentor
- Admin can view all chats between students and mentors



Login credentials:
Admin: admin@example.com / admin123
Mentors: [mentor-email](sarah.johnson@example.com) / mentor123
Student: student@example.com / student123
