'''
Created on Sep 26, 2014

@author: Matthew
'''
from django.views.generic import TemplateView
from twilio.rest import TwilioRestClient 
from django.http import HttpResponseRedirect
from django.http import HttpResponse
from django.shortcuts import render
from django.shortcuts import render_to_response
import urllib2
import urllib
from django.http import HttpResponse

from django.forms.formsets import formset_factory
import models
import django_twilio

def test_page(request):
    user = models.User(first_name="matt",last_name="maclean")
    user.save()
    return render(request, 'test.html')

def admin_home_page(request):
    pairs = []
    for pair in models.Pair.objects.all():
        mentor = models.User.objects.get(id=pair.mentor_id)
        mentor_name = mentor.first_name + " " + mentor.last_name
        mentee = models.User.objects.get(id=pair.mentee_id)
        mentee_name = mentee.first_name + " " + mentor.last_name
        dict = {"id": pair.id,
                "mentor_name": mentor_name,
                "mentee_name": mentee_name,
                "freq": 0}
        pairs.append(dict)
    return render(request, 'Admin_home_page.html', {"pairs": pairs})

def admin_history(request):
    return render(request, 'Admin_history.html')
def admin_mentor_mentee(request):
    return render(request, 'Admin_mentor_mentee.html')
def login_page(request):
    return render(request, 'login.html')
def mentor_view(request):
    print "getting page"
    return render(request, "Mentor_View.html")

def login_request(request):
    print "entering login request"
    email = request.GET.get('email')
    user = models.User.objects.filter(email=email)
    print user
    print email
    if len(user) == 0:
        return HttpResponse("Invalid username or password")
    user = user[0]
    if user.type == 2: #Admin
        return admin_home_page(request)
    if user.type == 1: #Mentor
        return mentor_view(request)
    if user.type == 0: # Mentee
        return mentor_view(request)
    return HttpResponse("invalid")

def view_pair_profile(request):
    pair_id = long(request.GET.get("pair_id"))
    return render(request, 'profile.html', {'pair_id': pair_id})
    
def view_history(request):
    print "in view history"
    pair_id = long(request.GET.get('pair_id'))
    print "here"
    pair = models.Pair.objects.get(id=pair_id)
    messages = models.Message.objects.filter(pair_id=pair_id)
    mentor = models.User.objects.get(id=pair.mentor_id)
    mentee = models.User.objects.get(id=pair.mentee_id)
    print"below"
    print len(messages)
    return render(request, 'Admin_history.html', {"messages": messages,
                                                  "mentor_id": pair.mentor_id,
                                                  "mentee_id": pair.mentee_id,
                                                  "mentor_name": mentor.first_name,
                                                  "mentee_name": mentee.first_name})

def route_message(request):
    print "in route message"
    phone_number_incoming = request.GET.get('From')
    text = request.GET.get('Body')
    print phone_number_incoming
    print "about to"
    user = models.User.objects.filter(phone_number=phone_number_incoming)
    print len(user)
    user = user[0]
    print "a"
    pair_cand_1 = models.Pair.objects.filter(mentor_id=user.id)
    print "b"
    pair_cand_2 = models.Pair.objects.filter(mentee_id=user.id)
    print "c"
    if pair_cand_1:
        mentee = models.User.objects.get(id=pair_cand_1[0].mentee_id)
        print "d"
        phone_number_target = mentee.phone_number
        user_to = mentee
        pair = pair_cand_1[0]
    else:
        mentor = models.User.objects.get(id=pair_cand_2[0].mentor_id)
        user_to=mentor
        print "e"
        phone_number_target = mentor.phone_number
        pair = pair_cand_2[0]
    print phone_number_target
    print user_to.id
    print user.id
    print pair.id
    message = models.Message(user_from=user, user_to=user_to, pair=pair,text=text)
    message.save()

    TWILIO_ACCOUNT_SID = 'ACa3784f71861749cee6445c4d2f182f27'
    TWILIO_AUTH_TOKEN = '7a474c787f36db39c3c08edce40598a2'
    client = TwilioRestClient(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN) 
    print "sending"
    client.messages.create( 
        from_="+17328100314",   
        to_=phone_number_target,
        body_=text,
    )
        
    #django_twilio.views.message(request, text, phone_number_incoming, '+17328100314', None, None, None, '/message/completed/')


    

    


def initialize_data(request):
    # Create mentor and mentee
    moses = models.User(first_name="Moses", last_name="Soh", email="moses.soh@gmail.com", phone_number="+12676487834", type=0)
    moses.save()
    matt = models.User(first_name="Matt", last_name="MacLean", email="matthewtmaclean@gmail.com", phone_number="+19086921924", type=1)
    matt.save()
    bryan = models.User(first_name="Bryan", last_name="Cam", email="bryanrcam@gmail.com", phone_number="+17862395770", type=2)
    bryan.save()
    # Create pairing
    pair = models.Pair(mentor=matt, mentee=moses, admin=bryan)
    pair.save()
    # Add messages
    message = models.Message(user_from=moses, user_to=matt, pair=pair,text="Hello Mentor")
    message.save()
    message = models.Message(user_from=matt, user_to=moses, pair=pair,text="Hello Mentee")
    message.save() 


