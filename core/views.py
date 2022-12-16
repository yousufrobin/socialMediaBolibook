from ast import Pass
from cProfile import Profile
from django.shortcuts import render, HttpResponse, redirect
from django.contrib import messages
from django.contrib.auth.models import User

from core.models import Follow, LikePost, Profile, Post
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from itertools import chain
import random


# Create your views here.
@login_required(login_url="signin")
def index(request):
    # the code below is used if "@login_required(login_url="signin")" is not present

    # if request.user.is_anonymous:
    #     return redirect("signin")
    # else:
    #     return render(request, "index.html")

    user = User.objects.get(username=request.user.username)
    user_profile_object = Profile.objects.get(user=user)
    # posts = Post.objects.all()

    users_that_loggedin_user_following_list = []
    feed = []

    users_that_loggedin_user_following = Follow.objects.filter(
        following_user=request.user.username
    )
    for user_that_loggedin_user_following in users_that_loggedin_user_following:
        users_that_loggedin_user_following_list.append(
            user_that_loggedin_user_following.followed_user
        )

    for username in users_that_loggedin_user_following_list:
        feed.append(Post.objects.filter(user=username))
        # all the posts that a single user (username) have are compiled and then appended like[[all_post_of_the_username]]
        # that's why itertool.chain() function is used to iter the appended lists within the list
    # print(feed)
    feed_list = list(chain(*feed))
    # print(feed_list)

    # user suggestion algorithm
    all_users = User.objects.all()
    all_following_user = []

    for user in users_that_loggedin_user_following:
        single_user_object = User.objects.get(username=user.followed_user)
        all_following_user.append(single_user_object)

    print(all_following_user)
    suggestion_list = [
        x for x in list(all_users) if (x not in list(all_following_user))
    ]
    print(suggestion_list)
    loggedin_user = User.objects.filter(username=request.user.username)
    final_suggestion_list = [
        x for x in list(suggestion_list) if (x not in list(loggedin_user))
    ]
    random.shuffle(final_suggestion_list)

    user_profile_ids = []
    user_profile_list = []

    for user_object in final_suggestion_list:
        user_profile_ids.append(user_object.id)
    for id in user_profile_ids:
        user_profile = Profile.objects.filter(id_user=id)
        user_profile_list.append(user_profile)

    ultimate_suggestion_list = list(chain(*user_profile_list))
    print(ultimate_suggestion_list)

    context = {
        "user_profile_object": user_profile_object,
        "posts": feed_list,
        "ultimate_suggestion_list": ultimate_suggestion_list[:4],
    }
    return render(request, "index.html", context)


@login_required(login_url="signin")
def upload(request):
    if request.method == "POST":
        if request.FILES.get("uploaded_image") == None:
            return redirect("/")
        elif request.FILES.get("uploaded_image") != None:
            user = request.user.username
            image = request.FILES.get("uploaded_image")
            caption = request.POST.get("caption")

            new_post = Post.objects.create(user=user, image=image, caption=caption)
            new_post.save()

            return redirect("/")

    elif request.method == "GET":
        return redirect("/")

    else:
        return redirect("/")


@login_required(login_url="signin")
def like_post(request):
    username = request.user.username
    post_id = request.GET.get("post_id")
    print(post_id)

    post = Post.objects.get(id=post_id)

    like_checker = LikePost.objects.filter(username=username, post_id=post_id).first()

    if like_checker == None:
        new_like = LikePost.objects.create(username=username, post_id=post_id)
        new_like.save()

        post.like_quantity = post.like_quantity + 1
        post.save()

        return redirect("/")

    else:
        like_checker.delete()

        post.like_quantity = post.like_quantity - 1
        post.save()

        return redirect("/")


@login_required(login_url="signin")
def setting(request):
    user_profile = Profile.objects.get(user=request.user)
    if request.method == "POST":
        if request.FILES.get("photo") == None:
            photo = user_profile.profileimg
            bio = request.POST.get("bio")
            location = request.POST.get("location")

            user_profile.profileimg = photo
            user_profile.bio = bio
            user_profile.location = location
            user_profile.save()

        elif request.FILES.get("photo") != None:
            photo = request.FILES.get("photo")
            bio = request.POST.get("bio")
            location = request.POST.get("location")

            user_profile.profileimg = photo
            user_profile.bio = bio
            user_profile.location = location
            user_profile.save()

        return redirect("setting")

    elif request.method == "GET":
        return render(request, "setting.html", {"user_profile": user_profile})

    else:
        return render(request, "setting.html", {"user_profile": user_profile})


@login_required(login_url="signin")
def profile(request, username):

    user_object = User.objects.get(username=username)

    profile = Profile.objects.get(user=user_object)
    # Or profile = Profile.objects.get(user=request.user)

    posts = Post.objects.filter(user=username)
    number_of_posts = len(posts)

    follower = request.user.username
    followed = username

    followeds = len(Follow.objects.filter(following_user=username))
    followers = len(Follow.objects.filter(followed_user=username))

    if Follow.objects.filter(following_user=follower, followed_user=followed).first():
        button_text = "Unfollow"
    else:
        button_text = "Follow"

    context = {
        "profile": profile,
        "user_object": user_object,
        "posts": posts,
        "number_of_posts": number_of_posts,
        "button_text": button_text,
        "followers": followers,
        "followeds": followeds,
    }
    return render(request, "profile.html", context)


@login_required(login_url="signin")
def follow(request):

    if request.method == "POST":
        follower = request.POST.get("follower")
        followed = request.POST.get("followed")
        if Follow.objects.filter(
            following_user=follower, followed_user=followed
        ).first():
            remove_follower = Follow.objects.get(
                following_user=follower, followed_user=followed
            )
            remove_follower.delete()
            return redirect("/profile/" + followed)
        else:
            create_follower = Follow.objects.create(
                following_user=follower, followed_user=followed
            )
            create_follower.save()

            return redirect("/profile/" + followed)

    elif request.method == "GET":
        return redirect("/")
    else:
        return redirect("/")


def signup(request):
    if request.method == "POST":
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        email = request.POST.get("email")
        username = request.POST.get("username")
        password = request.POST.get("password")
        password2 = request.POST.get("password2")

        if password == password2:
            if User.objects.filter(username=username).exists():
                messages.error(request, "This username already exsits!")
                return redirect("signup")

            elif User.objects.filter(email=email).exists():
                messages.error(request, "This email already exsits!")
                return redirect("signup")

            else:
                # user creation
                new_user = User.objects.create_user(
                    username=username, email=email, password=password
                )
                new_user.first_name = first_name
                new_user.last_name = last_name
                new_user.save()

                # user login immediately after the creation
                user = authenticate(username=username, password=password)
                login(request, user)

                # creating profile and redirecting to settings page
                user_model = User.objects.get(username=username)
                new_profile = Profile.objects.create(
                    user=user_model, id_user=user_model.id
                )
                new_profile.save()
                messages.success(
                    request, "You are successfully registered as a new user"
                )
                return redirect("setting")

        else:
            messages.error(request, "Passwords do not match!")
            return redirect("signup")

    elif request.method == "GET":
        return render(request, "signup.html")

    else:
        return HttpResponse("Something went wrong!")


def signin(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect("/")
        else:
            messages.warning(request, "Username or Password or Both Does not Match!")
            return render(request, "signin.html")

    elif request.method == "GET":
        return render(request, "signin.html")
    else:
        return render(request, "signin.html")


@login_required(login_url="signin")
def signout(request):
    logout(request)
    return redirect("signin")


@login_required(login_url="signin")
def search(request):
    if request.method == "POST":
        username = request.POST.get("username")
        searched_users = User.objects.filter(username__icontains=username)

        searched_user_profile_list = []

        for searched_user in searched_users:
            searched_user_profile = Profile.objects.get(user=searched_user)
            searched_user_profile_list.append(searched_user_profile)

        print(searched_user_profile_list)

        context = {
            "searched_user_profile_list": searched_user_profile_list,
            "username": username,
        }
        return render(request, "search.html", context)

    elif request.method == "GET":
        return redirect("/")

    else:
        return redirect("/")
