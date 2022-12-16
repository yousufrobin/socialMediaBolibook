from email.policy import default
from django.db import models
from django.contrib.auth import get_user_model
import uuid
from datetime import datetime

User = get_user_model()

# Create your models here.
class Profile(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    id_user = models.IntegerField()
    bio = models.TextField(blank=True)
    profileimg = models.ImageField(
        upload_to="profile_image", default="blank-profile-picture.png"
    )
    location = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return self.user.username


class Post(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    user = models.CharField(max_length=100)
    image = models.ImageField(upload_to="post_image")
    caption = models.TextField()
    create_time = models.DateTimeField(default=datetime.now)
    like_quantity = models.IntegerField(default=0)

    def __str__(self):
        return self.user


class LikePost(models.Model):
    username = models.CharField(max_length=100)
    post_id = models.CharField(max_length=500)

    def __str__(self):
        return self.username


class Follow(models.Model):
    following_user = models.CharField(max_length=100)
    followed_user = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.followed_user} is followed by {self.following_user}"
