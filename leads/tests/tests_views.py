from django.test import TestCase
from django.shortcuts import reverse

# Create your tests here.
class LandingPageTest(TestCase):
    #if create a method or fuction that starts with test it execute as one single test
    def test_status_code(self):
        # TODO some sort of test
        #making a request
        response = self.client.get(reverse("landing-page"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "landing.html")