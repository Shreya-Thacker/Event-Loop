"""
test_student_portal.py - Automated test suite verifying:
- Part 1: All 6 Student Portal frontend pages
- Part 2: All 3 Database Tables (student_login, student_registration, document_track)
- All CRUD Operations (Create, Read, Update, Delete)
"""
import io
import unittest
from app import create_app
from models import db, StudentLogin, StudentRegistration, DocumentTrack


class StudentPortalTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.app.config['WTF_CSRF_ENABLED'] = False
        self.client = self.app.test_client()

    def test_1_signup_page_and_crud_create(self):
        """Page 1 & Table 1/2 Create: Test Student Sign-up Page"""
        import uuid
        # GET page
        res = self.client.get('/student/signup')
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'Student Sign-Up', res.data)

        # POST create new student
        suffix = uuid.uuid4().hex[:6]
        unique_user = f'stu_{suffix}'
        unique_email = f'auto_{suffix}@adit.edu'
        res = self.client.post('/student/signup', data={
            'full_name': 'Automated Test Student',
            'username': unique_user,
            'email': unique_email,
            'phone': '9998887770',
            'password': 'TestPassword@123',
            'confirm_password': 'TestPassword@123'
        }, follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'Student account created successfully', res.data)

        # Verify DB records created
        with self.app.app_context():
            student = StudentLogin.query.filter_by(username=unique_user).first()
            self.assertIsNotNone(student)
            reg = StudentRegistration.query.filter_by(student_login_id=student.id).first()
            self.assertIsNotNone(reg)
            self.assertEqual(reg.registration_status, 'Draft')

    def test_2_login_and_auth(self):
        """Page 2: Test Student Login Page"""
        # GET page
        res = self.client.get('/student/login')
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'Student Login', res.data)

        # POST login with seeded student
        res = self.client.post('/student/login', data={
            'identifier': 'student@adit.edu',
            'password': 'Student@1234'
        }, follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'Student Hub', res.data)

    def test_3_forgot_password_flow(self):
        """Page 3: Test Forgot Password Page"""
        # GET page
        res = self.client.get('/student/forgot-password')
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'Forgot Password', res.data)

        # Step 1: Request reset code
        res = self.client.post('/student/forgot-password', data={
            'action': 'request_code',
            'email_or_id': 'student@adit.edu'
        }, follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'Verification code generated', res.data)

        # Retrieve token from DB
        with self.app.app_context():
            student = StudentLogin.query.filter_by(email='student@adit.edu').first()
            code = student.reset_token
            self.assertIsNotNone(code)

        # Step 2: Reset password
        res = self.client.post('/student/forgot-password', data={
            'action': 'reset_password',
            'email_or_id': 'student@adit.edu',
            'reset_code': code,
            'new_password': 'Student@1234',
            'confirm_password': 'Student@1234'
        }, follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'Password successfully reset', res.data)

    def test_4_registration_crud_read_update(self):
        """Page 4 & Table 2: Student Registration Page CRUD (Read & Update)"""
        # Login
        self.client.post('/student/login', data={
            'identifier': 'student@adit.edu',
            'password': 'Student@1234'
        })

        # GET registration form (CRUD Read)
        res = self.client.get('/student/registration')
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'Student Campus Registration', res.data)
        self.assertIn(b'A.D. Patel Institute of Technology', res.data)

        # POST update registration form (CRUD Update)
        res = self.client.post('/student/registration', data={
            'action': 'save_draft',
            'college_name': 'A.D. Patel Institute of Technology (ADIT)',
            'enrollment_no': '230010116001',
            'course_enrolled': 'B.Tech - Computer Engineering',
            'department': 'Computer Engineering',
            'full_name': 'Shreya Thacker',
            'phone_number': '9876543210',
            'primary_interests': 'Hackathons, Workshops, AI & ML',
            'skills': 'Python, Flask, React, Cloud',
            'permanent_address': 'V.V. Nagar',
            'city': 'Anand',
            'state': 'Gujarat',
            'pincode': '388120'
        }, follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'Registration draft saved successfully', res.data)

    def test_5_documents_crud_create_read_update_delete(self):
        """Page 5 & Table 3: Document Track Table Full CRUD"""
        # Login
        self.client.post('/student/login', data={
            'identifier': 'student@adit.edu',
            'password': 'Student@1234'
        })

        # 1. READ: Get documents page
        res = self.client.get('/student/documents')
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'Document Track Table', res.data)

        # 2. CREATE: Upload a test document
        dummy_file = (io.BytesIO(b'Test PDF campus document content'), 'sample_event_pass.pdf')
        res = self.client.post('/student/documents', data={
            'document_type': 'Workshop / Hackathon Registration Receipt',
            'remarks': 'Registration receipt for State Hackathon',
            'document_file': dummy_file
        }, content_type='multipart/form-data', follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'uploaded and recorded successfully', res.data)

        # Find uploaded doc ID from DB
        with self.app.app_context():
            doc = DocumentTrack.query.filter_by(
                document_type='Workshop / Hackathon Registration Receipt'
            ).order_by(DocumentTrack.id.desc()).first()
            self.assertIsNotNone(doc)
            doc_id = doc.id

        # 3. VIEW: View inline
        res = self.client.get(f'/student/documents/{doc_id}/view')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data, b'Test PDF campus document content')

        # 4. DOWNLOAD: Download attachment
        res = self.client.get(f'/student/documents/{doc_id}/download')
        self.assertEqual(res.status_code, 200)
        self.assertIn('attachment', res.headers.get('Content-Disposition', ''))

        # 5. UPDATE: Update remarks / replace file
        res = self.client.post(f'/student/documents/{doc_id}/update', data={
            'remarks': 'Updated receipt verification remarks'
        }, follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'updated successfully', res.data)

        # 6. DELETE: Delete document
        res = self.client.post(f'/student/documents/{doc_id}/delete', follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'deleted successfully from track records', res.data)

    def test_6_edit_profile_crud_update(self):
        """Page 6: Edit Current Profile Page (CRUD Update)"""
        # Login
        self.client.post('/student/login', data={
            'identifier': 'student@adit.edu',
            'password': 'Student@1234'
        })

        # GET page
        res = self.client.get('/student/edit-profile')
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'Campus & Event Profile', res.data)

        # POST update profile
        res = self.client.post('/student/edit-profile', data={
            'action': 'update_profile',
            'full_name': 'Shreya Thacker',
            'username': 'shreya_student',
            'email': 'student@adit.edu',
            'phone': '9876543210',
            'college_name': 'A.D. Patel Institute of Technology (ADIT)',
            'enrollment_no': '230010116001',
            'course_enrolled': 'B.Tech Information Technology',
            'department': 'Computer & IT Engineering',
            'primary_interests': 'Hackathons, AI & ML, Web Dev',
            'skills': 'Python, Flask, JavaScript, SQL'
        }, follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'Your profile has been updated successfully', res.data)


if __name__ == '__main__':
    unittest.main()
