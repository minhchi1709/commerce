from django.contrib.auth.models import AbstractUser
from django.db import models
from datetime import datetime

class User(AbstractUser):
    pass

class AuctionListing(models.Model):
    title = models.CharField(max_length=32)
    description = models.TextField(max_length=512)
    starting_bid = models.DecimalField(decimal_places=2, max_digits=10)
    url_img = models.URLField(default='https://upload.wikimedia.org/wikipedia/commons/a/ac/No_image_available.svg')
    category = models.CharField(max_length=32, default='No Category')
    created_time = models.DateTimeField(auto_now=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='have')
    watcher = models.ManyToManyField(User, blank=True, related_name="watchlist")
    sold_time = models.DateTimeField(auto_now=True)
    sold = models.BooleanField(default=False)
    sold_to = models.ForeignKey(User, blank=True, on_delete=models.CASCADE, related_name='buy')

    def __str__(self):
        return f'{self.title}, Price: {self.starting_bid}'
    
class Bid(models.Model):
    price = models.FloatField(default = 0)
    auction = models.ForeignKey(AuctionListing, on_delete=models.CASCADE, related_name="bids")
    bidder = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bids')

class Comment(models.Model):
    comment = models.TextField(max_length = 512)
    auction = models.ForeignKey(AuctionListing, on_delete=models.CASCADE, related_name="comments")
    commenter = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')

