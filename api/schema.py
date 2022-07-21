from django.contrib.auth.models import User
from django.utils import timezone
from graphene_django import DjangoObjectType
import graphene
import graphql_jwt

from api.models import Timeclock


class UserType(DjangoObjectType):
    class Meta:
        model = User
        fields = ("id", "username", "email")


class ClockType(DjangoObjectType):
    class Meta:
        model = Timeclock
        fields = ("id", "user", "clock_in", "clock_out", "hours")


class ClockedHours(graphene.ObjectType):
    today = graphene.Int()
    currentWeek = graphene.Int()
    currentMonth = graphene.Int()


def get_hours(clocks):
    return sum([i.hours for i in clocks])

class Query(graphene.ObjectType):
    me = graphene.Field(UserType)
    current_clock = graphene.Field(ClockType)
    clocked_hours = graphene.Field(ClockedHours)

    def resolve_me(self, info, **kwargs):
        user = info.context.user
        if user.is_authenticated:
            return user
        return None

    def resolve_current_clock(self, info, **kwargs):
        user = info.context.user
        if user.is_authenticated:
            timeclock = Timeclock.objects.filter(
                user_id=user.id, clock_out=None
            ).latest('-clock_in')
            return timeclock
        return None

    def resolve_clocked_hours(self, info, **kwargs):
        user = info.context.user
        if user.is_authenticated:
            clock_this_month = Timeclock.objects.filter(
                user_id=user.id, clock_in__month=timezone.now().month
            )
            month_hours = get_hours(clock_this_month)
            clock_this_week = clock_this_month.filter(
                clock_in__week=timezone.now().isocalendar()[1]
            )
            week_hours = get_hours(clock_this_week)
            clock_today = clock_this_week.filter(
                clock_in__date=timezone.now().date()
            )
            today_hours = get_hours(clock_today)
            return ClockedHours(
                today=today_hours, currentWeek=week_hours,
                currentMonth=month_hours
            )
        return ClockedHours(today=None, currentWeek=None, currentMonth=None)

############################## MUTATIONS ######################################
class CreateUser(graphene.Mutation):
    class Arguments:
        email = graphene.String()
        username = graphene.String()
        password = graphene.String()

    user = graphene.Field(UserType)

    def mutate(root, info, email, username, password):
        user = User.objects.create_user(
            email=email, username=username, password=password
        )
        return CreateUser(user=user)


class ClockIn(graphene.Mutation):

    clock = graphene.Field(ClockType)

    def mutate(root, info, **kwargs):
        user = info.context.user
        timeclock = None
        if user.is_authenticated:
            timeclock, created = Timeclock.objects.get_or_create(
                user_id=user.id, clock_in=timezone.now()
            )
        return ClockIn(clock=timeclock)


class ClockOut(graphene.Mutation):

    clock = graphene.Field(ClockType)

    def mutate(root, info, **kwargs):
        user = info.context.user
        timeclock = None
        if user.is_authenticated:
            timeclock = Timeclock.objects.filter(
                user_id=user.id
            ).last()
            if not timeclock.clock_out:
                timeclock.clock_out = timezone.now()
                timeclock.save()
        return ClockOut(clock=timeclock)


class Mutation(graphene.ObjectType):
    clockIn = ClockIn.Field()
    createUser = CreateUser.Field()
    clockOut = ClockOut.Field()
    obtain_token = graphql_jwt.ObtainJSONWebToken.Field()
    verify_token = graphql_jwt.Verify.Field()
    refresh_token = graphql_jwt.Refresh.Field()


schema = graphene.Schema(query=Query, mutation=Mutation)
