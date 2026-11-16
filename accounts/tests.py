from django.test import TestCase
from django.urls import reverse

from .models import User


class AccountTests(TestCase):
    def setUp(self):
        self.student = User.objects.create_user(
            'juan', 'juan@example.com', 'StrongPass123', first_name='Juan', last_name='Cruz')
        self.admin = User.objects.create_superuser('boss', 'boss@example.com', 'StrongPass123')

    def reg_data(self, **over):
        data = {
            'first_name': 'Maria', 'last_name': 'Santos', 'username': 'maria',
            'email': 'maria@example.com', 'password1': 'StrongPass123', 'password2': 'StrongPass123',
        }
        data.update(over)
        return data

    # ---- registration ----
    def test_register_success_hashes_password_and_sets_student(self):
        res = self.client.post(reverse('accounts:register'), self.reg_data())
        self.assertRedirects(res, reverse('accounts:login'))
        user = User.objects.get(username='maria')
        self.assertEqual(user.role, User.Role.STUDENT)
        self.assertNotEqual(user.password, 'StrongPass123')
        self.assertTrue(user.check_password('StrongPass123'))

    def test_register_password_mismatch(self):
        res = self.client.post(reverse('accounts:register'), self.reg_data(password2='Different123'))
        self.assertEqual(res.status_code, 200)
        self.assertFalse(User.objects.filter(username='maria').exists())

    def test_register_required_fields(self):
        res = self.client.post(reverse('accounts:register'), self.reg_data(first_name='', email=''))
        self.assertFalse(User.objects.filter(username='maria').exists())
        self.assertContains(res, 'This field is required')

    def test_register_invalid_email(self):
        self.client.post(reverse('accounts:register'), self.reg_data(email='not-an-email'))
        self.assertFalse(User.objects.filter(username='maria').exists())

    def test_register_duplicate_username(self):
        self.client.post(reverse('accounts:register'), self.reg_data(username='juan'))
        self.assertEqual(User.objects.filter(username='juan').count(), 1)

    def test_register_duplicate_email_any_case(self):
        res = self.client.post(reverse('accounts:register'), self.reg_data(email='JUAN@example.com'))
        self.assertContains(res, 'already exists')
        self.assertFalse(User.objects.filter(username='maria').exists())

    def test_cannot_register_as_admin(self):
        self.client.post(reverse('accounts:register'), self.reg_data(role='ADMIN'))
        self.assertEqual(User.objects.get(username='maria').role, User.Role.STUDENT)

    # ---- login / logout ----
    def test_login_valid_goes_to_role_dashboard(self):
        res = self.client.post(reverse('accounts:login'), {'username': 'juan', 'password': 'StrongPass123'}, follow=True)
        self.assertEqual(res.redirect_chain[-1][0], reverse('accounts:student_dashboard'))

    def test_admin_login_goes_to_admin_dashboard(self):
        res = self.client.post(reverse('accounts:login'), {'username': 'boss', 'password': 'StrongPass123'}, follow=True)
        self.assertEqual(res.redirect_chain[-1][0], reverse('accounts:admin_dashboard'))

    def test_login_invalid_shows_error(self):
        res = self.client.post(reverse('accounts:login'), {'username': 'juan', 'password': 'wrong'})
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, 'Invalid username or password')

    def test_logout_ends_session(self):
        self.client.login(username='juan', password='StrongPass123')
        self.client.post(reverse('accounts:logout'))
        res = self.client.get(reverse('accounts:profile'))
        self.assertEqual(res.status_code, 302)
        self.assertIn(reverse('accounts:login'), res.url)

    def test_protected_pages_redirect_to_login(self):
        for name in ['dashboard', 'student_dashboard', 'admin_dashboard', 'profile', 'profile_edit']:
            res = self.client.get(reverse(f'accounts:{name}'))
            self.assertEqual(res.status_code, 302, name)
            self.assertIn(reverse('accounts:login'), res.url, name)

    # ---- roles ----
    def test_student_cannot_open_admin_dashboard(self):
        self.client.login(username='juan', password='StrongPass123')
        res = self.client.get(reverse('accounts:admin_dashboard'))
        self.assertRedirects(res, reverse('accounts:dashboard'), target_status_code=302)

    def test_admin_cannot_open_student_dashboard(self):
        self.client.login(username='boss', password='StrongPass123')
        res = self.client.get(reverse('accounts:student_dashboard'))
        self.assertRedirects(res, reverse('accounts:dashboard'), target_status_code=302)

    def test_createsuperuser_gets_admin_role(self):
        self.assertEqual(self.admin.role, User.Role.ADMIN)

    # ---- profile ----
    def test_profile_shows_own_info(self):
        self.client.login(username='juan', password='StrongPass123')
        res = self.client.get(reverse('accounts:profile'))
        self.assertContains(res, 'juan@example.com')
        self.assertNotContains(res, 'boss@example.com')

    def test_profile_update(self):
        self.client.login(username='juan', password='StrongPass123')
        res = self.client.post(reverse('accounts:profile_edit'), {
            'first_name': 'Juan', 'last_name': 'Dela Cruz', 'email': 'juan2@example.com',
            'contact_number': '09171234567', 'course_year': 'BSIT-3', 'bio': 'Hello',
        })
        self.assertRedirects(res, reverse('accounts:profile'))
        self.student.refresh_from_db()
        self.assertEqual(self.student.last_name, 'Dela Cruz')
        self.assertEqual(self.student.contact_number, '09171234567')

    def test_profile_update_rejects_other_users_email(self):
        self.client.login(username='juan', password='StrongPass123')
        res = self.client.post(reverse('accounts:profile_edit'), {
            'first_name': 'Juan', 'last_name': 'Cruz', 'email': 'boss@example.com'})
        self.assertContains(res, 'already used')
        self.student.refresh_from_db()
        self.assertEqual(self.student.email, 'juan@example.com')

    def test_profile_edit_only_changes_own_account(self):
        self.client.login(username='juan', password='StrongPass123')
        self.client.post(reverse('accounts:profile_edit'), {
            'first_name': 'Hacked', 'last_name': 'Name', 'email': 'juan@example.com'})
        self.admin.refresh_from_db()
        self.assertNotEqual(self.admin.first_name, 'Hacked')
