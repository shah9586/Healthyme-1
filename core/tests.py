from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from unittest.mock import patch

from core.views import analyze_product_text

User = get_user_model()


class HealthyMeViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="testuser@gmail.com",
            email="testuser@gmail.com",
            contact="9999999999",
            password="Test@123"
        )

    def test_home_page_loads(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)

    def test_login_page_loads(self):
        response = self.client.get("/login/")
        self.assertEqual(response.status_code, 200)

    def test_register_page_loads(self):
        response = self.client.get("/register/")
        self.assertEqual(response.status_code, 200)

    def test_register_user(self):
        response = self.client.post("/register/", {
            "first_name": "Princy",
            "last_name": "Shah",
            "email": "newuser@gmail.com",
            "contact": "8888888888",
            "password1": "Strong@123",
            "password2": "Strong@123"
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(email="newuser@gmail.com").exists())

    def test_login_user(self):
        response = self.client.post("/login/", {
            "username": "testuser@gmail.com",
            "password": "Test@123"
        })
        self.assertEqual(response.status_code, 302)

    def test_scan_requires_login(self):
        response = self.client.get("/scan/")
        self.assertEqual(response.status_code, 302)

    def test_scan_page_loads_after_login(self):
        self.client.login(username="testuser@gmail.com", password="Test@123")
        response = self.client.get("/scan/")
        self.assertEqual(response.status_code, 200)

    @patch("core.views.fetch_product_advanced")
    def test_barcode_scan_success(self, mock_fetch_product):
        self.client.login(username="testuser@gmail.com", password="Test@123")

        mock_fetch_product.return_value = {
            "product_name": "Amul Milk",
            "text": "milk vitamin a vitamin d calcium protein",
            "lookup_source": "local dataset"
        }

        response = self.client.post("/scan/", {
            "barcode": "8901262200196"
        })

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Amul Milk")
        self.assertContains(response, "HealthyMe Analysis")

    @patch("core.views.fetch_product_advanced")
    def test_product_name_search_success(self, mock_fetch_product):
        self.client.login(username="testuser@gmail.com", password="Test@123")

        mock_fetch_product.return_value = {
            "product_name": "Parle-G Biscuit",
            "text": "refined wheat flour sugar palm oil milk solids",
            "lookup_source": "product name"
        }

        response = self.client.post("/scan/", {
            "product_name": "Parle-G"
        })

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Parle-G Biscuit")

    @patch("core.views.fetch_product_advanced")
    def test_product_not_found(self, mock_fetch_product):
        self.client.login(username="testuser@gmail.com", password="Test@123")

        mock_fetch_product.return_value = None

        response = self.client.post("/scan/", {
            "barcode": "0000000000000"
        })

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Product Not Found")

    def test_analyze_product_text_unhealthy(self):
        result = analyze_product_text(
            "refined wheat flour sugar palm oil preservatives artificial color",
            product_name="Hide & Seek Biscuit"
        )

        self.assertEqual(result["status"], "Unhealthy ❌")
        self.assertTrue(len(result["issues"]) > 0)

    def test_analyze_product_text_healthy(self):
        result = analyze_product_text(
            "milk protein calcium vitamin d",
            product_name="Amul Milk"
        )

        self.assertIn(result["status"], ["Healthy ✅", "Moderate ⚠️"])
        self.assertTrue(result["score"] is not None)