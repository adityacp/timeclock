import json
from graphene_django.utils.testing import GraphQLTestCase
from django.contrib.auth.models import User


class TimeClockTestCase(GraphQLTestCase):

    GRAPHQL_URL = "/graphql"

    def setUp(self):
        User.objects.create_user(
            username="test_user1", password="test_user1",
            email="test@mail.com"
        )
        response = self.query(
            '''
            mutation {
                obtainToken(username: "test_user1", password: "test_user1") {
                    token
                    payload
                    refreshExpiresIn
                }
            }
            '''
        )
        content = json.loads(response.content)
        self.token = content.get("data").get("obtainToken").get("token")

    def test_clockin_mutation(self):
        response = self.query(
            '''
            mutation {
                clockIn {
                    clock {
                    user {
                        email
                    }
                    clockIn
                    clockOut
                    }
                }
            }
            ''',
            headers={'HTTP_AUTHORIZATION': f'JWT {self.token}'}
        )

        content = json.loads(response.content)
        timeclock = content.get("data", {}).get("clockIn", {}).get("clock", {})
        user_email = timeclock.get("user", {}).get("email", "")
        clock_out = timeclock.get("clockOut", None)
        self.assertResponseNoErrors(response)
        self.assertEqual(user_email, "test@mail.com")
        self.assertEqual(clock_out, None)


    def test_clock_out_mutation(self):
        self.query(
            '''
            mutation {
                clockIn {
                    clock {
                    user {
                        email
                    }
                    clockIn
                    clockOut
                    }
                }
            }
            ''',
            headers={'HTTP_AUTHORIZATION': f'JWT {self.token}'}
        )
        response = self.query(
            '''
            mutation {
                clockOut {
                    clock {
                    user {
                        email
                    }
                    clockIn
                    clockOut
                    }
                }
            }
            ''',
            headers={'HTTP_AUTHORIZATION': f'JWT {self.token}'}
        )

        content = json.loads(response.content)
        timeclock = content.get("data", {}).get("clockOut", {}).get("clock", {})
        user_email = timeclock.get("user", {}).get("email", "")
        clock_out = timeclock.get("clockOut", None)
        self.assertResponseNoErrors(response)
        self.assertEqual(user_email, "test@mail.com")
        self.assertNotEqual(clock_out, None)

    def test_aggregation_query(self):
        response = self.query(
            '''
            query {
                clockedHours {
                    today
                    currentWeek
                    currentMonth
                }
            }
            ''',
            headers={'HTTP_AUTHORIZATION': f'JWT {self.token}'}
        )
        content = json.loads(response.content)
        clocked_hours = content.get("data", {}).get("clockedHours")
        self.assertEqual(clocked_hours.get("today"), 0)
        self.assertEqual(clocked_hours.get("currentWeek"), 0)
        self.assertEqual(clocked_hours.get("currentMonth"), 0)
        self.assertResponseNoErrors(response)
