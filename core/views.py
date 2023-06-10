from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from item.models import Category, Item
from .forms import SignupForm, LoginForm
from .models import Order, Order_Item, User, Userimage, Camera_image
# from django.contrib.User import User
import io
from django.conf import settings
import numpy as np
import face_recognition
from PIL import Image
import urllib.request as ur

import base64
from base64 import decodestring, b64decode

# Create your views here.
def index(request):
    recommended = []
    if request.user.is_authenticated:
        customer = User.objects.get(username=request.user.username)
        recommended_category = get_user_preferred_category(customer)
        if recommended_category:
        # profile = Profile.objects.get(user=customer)
        # recommended_category = profile.preferred_category
            recommended_all = Item.objects.filter(category=recommended_category)

            order = Order.objects.get(user=customer)
            items = Order_Item.objects.filter(order=order)

            for item in recommended_all:
                if item not in items:
                    recommended.append(item)
                if len(recommended)==3:
                    break

    items = Item.objects.all().order_by('price')#.values()
    categories = Category.objects.all()

    a = dict()
    a['items'] = items
    a['categories'] = categories
    a['count'] = int(len(recommended))
    a['recommended'] = recommended

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
            user = User.objects.get(username=username)
            order = Order(user=user)
            order.save()
            user_img = Userimage(user=user, img=image)
            user_img.save()
            # profile = Profile(user=user)
            # profile.save()
            user = authenticate(username=username,password=password1)
            login(request,user)        
            return redirect('/')
        else:
            a=dict()
            a['form'] = form
            return render(request, 'core/signup.html', context=a)
        
    else:
        form = SignupForm()
        
    a=dict()
    a['form'] = form
    return render(request, 'core/signup.html', context=a)


# def login_view(request):
#     if request.method == 'POST':
#         form = LoginForm(request.POST, request.FILES)
#         # print(form)
#         print('ishan  ',request.POST.get("img"))
#         if form.is_valid():
#             # form.save()
#             print(123)
#             username = form.cleaned_data["username"]
#             password = form.cleaned_data["password"]
#             img = form.cleaned_data["img"]
#             user = authenticate(request, username=username, password=password)
#             if user is not None:
#                 # customer = User.objects.get(username=username)
#                 customer=user
#                 img = img.replace('data:image/png;base64,', '') 
#                 # if face_detect(img, customer):
#                 if test_compare_images(user, Userimage.objects.get(user=customer).img.path,img,0.8):
#                     login(request, user)
#                     # get_user_preferred_category(customer)
#                     return redirect('/')
#                 else:
#                     form = LoginForm()
#                     return render(request, "core/login.html", {'message': 'Face does not match with your credentials.', 'form': form})
#             else:
#                 form = LoginForm()
#                 return render(request, "core/login.html", {'message': 'Username and Password does not match.', 'form': form})

#     else:
#         form = LoginForm()
#         return render(request, "core/login.html", {'form': form})
def login_view(request):
    if request.method == 'POST':
        # if form.is_valid():
        # print(123)
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            img = request.POST.get("img")
            img = img.replace('data:image/png;base64,', '')
            customer = user
            if test_compare_faces(Userimage.objects.get(user=customer).img.path, img):
                login(request, user)
                return redirect('/')
            else:
                form = LoginForm()
                # form.add_error(None, 'Face does not match with your credentials.')
        else:
            form = LoginForm()
            # form.add_error(None, 'Username and Password do not match.')
    else:
        form = LoginForm()

    return render(request, "core/login.html", {'form': form})

def login_view2(request):
    if request.method == 'POST':
        # print(request.POST.dict())
        form = LoginForm(request.POST)
        print(form)
        if form.is_valid():
            print(123)
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            user = authenticate(request, username=username, password=password)
            if user is not None:
                img = form.cleaned_data.get("img")
                img = img.replace('data:image/png;base64,', '')
                customer = user
                if test_compare_images(user, Userimage.objects.get(user=customer).img.path, img, 0.8):
                    login(request, user)
                    return redirect('/')
                else:
                    form = LoginForm()
                    form.add_error('img', 'Face does not match with your credentials.')
            else:
                form = LoginForm()
                form.add_error(None, 'Username and Password do not match.')
        else:
            # Handle the case when the form is not valid
            # print("invalid form")
            # print(form.errors) 
            form = LoginForm()
            # return render(request, "core/login.html", {'form': form})
    else:
        form = LoginForm()

    return render(request, "core/login.html", {'form': form})
    
# import face_recognition
# from PIL import Image
import io
from urllib.request import urlopen
import tempfile
from base64 import decodestring


import base64
import io
from PIL import Image

def convert_base64_to_image(base64_string):
    # Decode the base64 string into binary data
    image_data = base64.b64decode(base64_string)

    # Create a BytesIO stream to work with the binary data
    stream = io.BytesIO(image_data)

    # Open the image using PIL (Python Imaging Library)
    image = Image.open(stream)

    return image

# Example usage
# base64_string = "your_base64_encoded_image_string"

# Convert base64 to image
# image = convert_base64_to_image(base64_string)

# image_path = "path_to_save_image.jpg"  # Provide the desired file path
# image.save(image_path, "JPEG")


# def test_face_detect(url_image, png_image_path):
#     import face_recognition

import uuid
from django.core.files.base import ContentFile

def convert_base64_to_image(base64_string):
    # Decode the base64 string into binary data
    image_data = base64.b64decode(base64_string)

    # Create a BytesIO stream to work with the binary data
    stream = io.BytesIO(image_data)

    # Open the image using PIL (Python Imaging Library)
    image = Image.open(stream)

    return image

# def base64_file(data, name=None):
#     _format, _img_str = data.split(';base64,')
#     _name, ext = _format.split('/')
#     # if not name:
#     #     name = _name.split(":")[-1]
#     filename = str(uuid.uuid4())
#     return ContentFile(base64.b64decode(_img_str), name='{}.{}'.format(filename, 'jpeg')), filename
import cv2
def test_compare_faces(jpeg_image_path, base64_image):
    # Load the JPEG image
    jpeg_image = cv2.imread(jpeg_image_path)

    # Convert the base64 image to numpy array
    base64_image = base64_image.split(';base64,')[1]
    # print(base64_image)
    base64_data = base64.b64decode(base64_image)
    nparr = np.frombuffer(base64_data, np.uint8)
    base64_image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    # Convert the images to RGB format
    jpeg_image_rgb = cv2.cvtColor(jpeg_image, cv2.COLOR_BGR2RGB)
    base64_image_rgb = cv2.cvtColor(base64_image, cv2.COLOR_BGR2RGB)

    # Detect faces in the images
    jpeg_face_locations = face_recognition.face_locations(jpeg_image_rgb)
    base64_face_locations = face_recognition.face_locations(base64_image_rgb)

    # Encode the face landmarks
    jpeg_face_encodings = face_recognition.face_encodings(jpeg_image_rgb, jpeg_face_locations)
    base64_face_encodings = face_recognition.face_encodings(base64_image_rgb, base64_face_locations)

    if len(base64_face_encodings)==0:
        return False

    # Compare the face encodings
    results = face_recognition.compare_faces(jpeg_face_encodings, base64_face_encodings[0])

    return results


def test_compare_images(user, registered_image, login_image, threshold):
    # return True
    # Load the images
    # print(login_image)
    login_image = login_image[login_image.find(",")+1:]
    # login_image = convert_base64_to_image(login_image)
    # login_image = ContentFile(base64.b64decode(login_image))
    filename = str(uuid.uuid4())

    image = convert_base64_to_image(login_image)

    cam_img =Camera_image(user=user, img=image)
    cam_img.save()
    # cam_img.img.save('{}.png'.format(filename), login_image)

    login_image_path = cam_img.img.path

    registered_image = face_recognition.load_image_file(registered_image)

    # login_image = ur.urlopen(login_image_path)
    login_image = face_recognition.load_image_file(login_image_path)

    # Generate face encodings
    registered_encoding = face_recognition.face_encodings(registered_image)[0]
    login_encoding = face_recognition.face_encodings(login_image)[0]

    # Compare the face encodings
    face_distance = face_recognition.face_distance([registered_encoding], login_encoding)
    similarity_score = 1 - face_distance

    # Compare the similarity score with the threshold
    if similarity_score > threshold:
        return True  # Images match
    else:
        return False  # Images do not match

    # # Example usage
    # registered_image_path = 'path_to_registered_image.jpg'
    # login_image_path = 'path_to_login_image.jpg'
    # threshold = 0.6  # Adjust the threshold as per your requirements

    # if compare_images(registered_image_path, login_image_path, threshold):
    #     print("Login successful!")
    # else:
    #     print("Login failed. Images do not match.")



def face_detect(camera_image,stored_image):
    # Load the stored image using face_recognition
    # path = stored_image.image.path
    # print(path)
    path = Userimage.objects.get(user=stored_image).img.path
    print(path)
    # print(camera_image)
    # path = path.split('media')
    # new_path = path[0]+'media'+path[-1]
    stored_image = face_recognition.load_image_file(path)
    # face_1_image = face_recognition.load_image_file(stored_image.image.path)
    face_1_face_encoding = face_recognition.face_encodings(stored_image)[0]

    # Convert the camera image bytes to a NumPy array
    camera_image = ur.urlopen(camera_image)
    camera_image = face_recognition.load_image_file(camera_image)

    # Encode the faces in the images
    face_locations = face_recognition.face_locations(camera_image)
    # captured_face_encoding = face_recognition.face_encodings(camera_image)[0]
    face_encodings = face_recognition.face_encodings(camera_image, face_locations)
    
    # stored_face_encoding = face_recognition.face_encodings(stored_image)[0]

    # Compare the face encodings
    if(len(face_encodings)==0):
        return False
    check=face_recognition.compare_faces(face_1_face_encoding, face_encodings)
    print(check)
    if check:
        return True
    return False
    # return results[0]  # Return the result (True or False)

def logout_view(request):
    logout(request)
    return redirect('/')

def learning(request):
    if request.user.is_authenticated:
        customer = User.objects.filter(username=request.user.username)[0]
        order = Order.objects.get(user=customer)
        items = Order_Item.objects.filter(order=order)
    else:
        form = LoginForm()
        return render(request, "core/login.html", {'form': form})
    
    return render(request, 'core/cart.html', {'items': items})

def get_user_preferred_category(user):
    # try:
    #     profile = Profile.objects.get(user=user)
    # except:
    #     return 
    order = Order.objects.get(user=user)
    purchased_courses = Order_Item.objects.filter(order=order)

    # Count the occurrences of each category in purchased courses
    category_counts = {}
    for course in purchased_courses:
        category_counts[course.item.category] = category_counts.get(course.item.category, 0) + 1

    # Find the category with the maximum count
    if len(category_counts)>0:
        preferred_category = max(category_counts, key=category_counts.get)

        return preferred_category
    return False