from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from item.models import Category, Item
from .forms import SignupForm, LoginForm
from .models import Customer
# import os
from django.conf import settings
import numpy as np
import face_recognition
# from PIL import Image
import urllib.request as ur

import base64
from base64 import decodestring, b64decode

# Create your views here.
def index(request):
    items = Item.objects.all()
    categories = Category.objects.all()

    a = dict()
    a['items'] = items
    a['categories'] = categories

    return render(request, 'core/index.html', context=a)

def contact(request):
    return render(request, 'core/contact.html')

def signup(request):
    if request.method == 'POST':
        form = SignupForm(request.POST, request.FILES)

        if form.is_valid():
            form.save()
            username = form.cleaned_data.get("username")
            email = form.cleaned_data.get("email")
            password1 = form.cleaned_data.get("password1")
            password2 = form.cleaned_data.get("password2")
            image = form.cleaned_data.get("image")

            # obj = Customer.objects.create(
            #     username = username,
            #     email = email,
            #     password1 = password1,
            #     password2 = password2,
            #     image = image
            # )
            # obj.save()
            user = authenticate(username=username,password=password1)
            login(request,user)        
            return redirect('/')
        else:
            return redirect('/')
        
    else:
        form = SignupForm()
        
    a=dict()
    a['form'] = form
    return render(request, 'core/signup.html', context=a)

# def login(request):
#     if request.method == 'POST':
#         username = request.POST.get("username")
#         password = request.POST.get("password")

#         # print(username,password)
#         customer = Customer.objects.filter(username=username, password1=password)
#         # print(customer)
#         if not customer:
#             message = 'Incorrect Credentials'
#             return render(request, 'core/login.html', {'message': message, 'form': LoginForm(), 'error': message})
#         else:
#             # request.session['image'] = customer[0].image
#             request.session['username'] = username
#             request.session['passw'] = password
#             return redirect('/face_authentication')

#     else:
#         form = LoginForm()

#     return render(request, 'core/login.html', {'form': form})


# def face_authentication(request):
#     if request.method == 'POST':
#         img = str(request.POST.get("img"))
#         img1 = ur.urlopen(img)
#         img1 = face_recognition.load_image_file(img1)

#         customer = Customer.objects.filter(username=request.session['username'], password1=request.session['passw'])

#         customer[0].image.open()

#         face_1_image = face_recognition.load_image_file(customer[0].image)
#         face_1_face_encoding = face_recognition.face_encodings(face_1_image)[0]

#         face_locations = face_recognition.face_locations(img1)
#         face_encodings = face_recognition.face_encodings(img1, face_locations)

#         if(len(face_encodings)==0):
#             return render(request, 'core/face_authentication.html', {'message': 'Face not detected in Camera. Please try again.'})

#         check=face_recognition.compare_faces(face_1_face_encoding, face_encodings, tolerance=0.6)
#         request.session['authenticated'] = True
#         items = Item.objects.all()
#         categories = Category.objects.all()

#         a = dict()
#         a['items'] = items
#         a['categories'] = categories
#         a['authenticated'] = True
#         return render(request, 'core/index.html', a)

#     return render(request, 'core/face_authentication.html')

# def logout(request):
#     items = Item.objects.all()
#     categories = Category.objects.all()

#     a = dict()
#     a['items'] = items
#     a['categories'] = categories
#     a['authenticated'] = False

#     return render(request, 'core/index.html', context=a)

def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid:
            username = request.POST['username']
            password = request.POST['password']
            img = str(request.POST.get("img"))
            user = authenticate(request, username=username, password=password)
            if user is not None:
                customer = Customer.objects.filter(username=username, password1=password)
                if face_detect(img, customer):
                    login(request, user)
                    return redirect('/')
                else:
                    form = LoginForm()
                    return render(request, "core/login.html", {'message': 'Face does not match with your credentials.', 'form': form})
            else:
                form = LoginForm()
                return render(request, "core/login.html", {'message': 'Username and Password does not match.', 'form': form})

    else:
        form = LoginForm()
        return render(request, "core/login.html", {'form': form})

def face_detect(a,b):
    b[0].image.open()
    face_1_image = face_recognition.load_image_file(b[0].image)
    face_1_face_encoding = face_recognition.face_encodings(face_1_image)[0]

    a = ur.urlopen(a)
    a = face_recognition.load_image_file(a)
    face_locations = face_recognition.face_locations(a)
    face_encodings = face_recognition.face_encodings(a, face_locations)

    if(len(face_encodings)==0):
        return False
    check=face_recognition.compare_faces(face_1_face_encoding, face_encodings, tolerance=0.6)
    if check:
        return True
    return False

def logout_view(request):
    logout(request)
    return redirect('/')