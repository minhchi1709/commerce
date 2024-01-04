from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from datetime import datetime

from .models import User, AuctionListing, Bid, Comment

def close(request, listing_id):
    listing = AuctionListing.objects.get(id=listing_id)
    max_bid = 0
    bidder = None
    bids = listing.bids.all()
    for bid in bids:
        if max_bid < bid.price:
            max_bid = bid.price
            bidder = bid.bidder
    listing.sold_time = datetime.now()
    listing.sold = True
    listing.sold_to = bidder
    listing.save()
    return HttpResponseRedirect(reverse('index'))
        

def edit(request, listing_id):
    auction = AuctionListing.objects.all().get(pk = listing_id)
    if request.method == "POST":
        title = request.POST['title']
        description = request.POST['description']
        try:
            price = float(request.POST['bid'])
        except:
            ValueError('Please provide a float number for starting bid')
        url_img = request.POST['img']
        if not url_img:
            url_img = 'https://upload.wikimedia.org/wikipedia/commons/a/ac/No_image_available.svg'
        category = request.POST['category']
        if not category:
            category = 'No Category'
        auction.title = title
        auction.description = description
        auction.starting_bid = price
        auction.url_img = url_img
        auction.category = category
        auction.save()
        return HttpResponseRedirect(reverse('index'))
    return render(request, 'auctions/edit_listing.html', {
        "listing": auction
    })

def own_listings(request):
    user = request.user
    listings = AuctionListing.objects.all().filter(owner = user)
    return render(request, 'auctions/own_listings.html', {
        'auctions': listings
    })


def add_comment(request, listing_id):
    if request.method == "POST":
        comment = request.POST['comment']
        if comment:
            l = AuctionListing.objects.all().get(pk = listing_id)
            user = request.user
            Comment(comment=comment, auction=l, commenter=user).save()
    return HttpResponseRedirect(reverse('listing', args=(listing_id, )))

def category(request):
    listings = AuctionListing.objects.all()
    categories = [auctionlisting.category for auctionlisting in listings]
    categories.sort()
    categories = set(categories)
    if 'No Category' in categories:
        categories.remove('No Category')
        categories = list(categories)
        categories.append('No Category')
    listings_by_category = []
    for cate in categories:
        temp = []
        for l in listings:
            if l.category == cate:
                temp.append(l)
        listings_by_category.append({'category': cate, 'listings': temp})
    return render(request, 'auctions/category.html', {
        'listings_by_category': listings_by_category
    })

def show_watchlist(request):
    user = request.user
    return render(request, 'auctions/show_watchlist.html', {
        'watchlist': user.watchlist.all()
    })


def add_to_watchlist(request, listing_id):
    user = request.user
    if request.method == 'POST':
        auction_listing = AuctionListing.objects.all().get(id = listing_id)
        auction_listing.watcher.add(user)
    return HttpResponseRedirect(reverse('listing', args=(listing_id,)))

def bid(request, listing_id):
    user = request.user
    if request.method == "POST":
        bid = request.POST['bid']
        if not bid:
            return render(request, 'auctions/failure.html', {
                'msg': 'Provide a valid bid'
            })
        try:
            bid = float(bid)
        except:
            ValueError()
            return render(request, 'auctions/failure.html', {
                'msg': 'Your bid must be a float number'
            })
        auction_listing = AuctionListing.objects.all().get(id = listing_id)
        if bid < auction_listing.starting_bid:
            return render(request, 'auctions/failure.html', {
                'msg': f'Your bid must bigger than the starting bid {auction_listing.starting_bid}'
            })
        all_bids = auction_listing.bids.all()
        if len(all_bids) > 0:
            max_bid = max(single_bid.price for single_bid in all_bids)
            if bid <= max_bid:
                return render(request, 'auctions/failure.html', {
                'msg': f'Your bid must bigger than the current max bid {max_bid}'
            })
        Bid(price=bid, auction=auction_listing, bidder = user).save()
        return HttpResponseRedirect(reverse('listing', args=(listing_id,)))
    return HttpResponseRedirect(reverse('index'))

def listing(request, listing_id):
    user = request.user
    if not user.is_authenticated:
        return HttpResponseRedirect(reverse('index'))
    listing = AuctionListing.objects.get(id=listing_id)
    already_watched = len(listing.watcher.all().filter(id = user.id)) == 1
    max_bid = 0
    bidder = ''
    current_max_bid = 0
    if len(listing.bids.all()) == 0:
        already_bid = False
    else:
        bids = listing.bids.all()
        already_bid = False
        for bid in bids:
            if max_bid < bid.price:
                max_bid = bid.price
                bidder = bid.bidder.username
            if bid.bidder.id == user.id and bid.price > current_max_bid:
                current_max_bid = bid.price
            already_bid = already_bid or bid.bidder.id == user.id
    comments = listing.comments.all()
    
    return render(request, 'auctions/show_listing.html', {
        'listing': listing,
        'already_watched': already_watched,
        'already_bid': already_bid,
        'num_of_bids': len(listing.bids.all()),
        'owner': listing.owner.id == user.id,
        'max_bid': max_bid,
        'bidder': bidder,
        'current_max_bid': current_max_bid,
        'comments': comments
    })

def create_listing(request):
    if request.method == "POST": 
        title = request.POST['title']
        description = request.POST['description']
        try:
            price = float(request.POST['bid'])
        except:
            ValueError('Please provide a float number for starting bid')
        url_img = request.POST['img']
        if not url_img:
            url_img = 'https://upload.wikimedia.org/wikipedia/commons/a/ac/No_image_available.svg'
        category = request.POST['category']
        if not category:
            category = 'No Category'
        user = request.user
        AuctionListing(title = title, description=description, starting_bid = price, url_img = url_img, category = category,
                       owner = user, sold_to = user).save()
        return HttpResponseRedirect(reverse('index'))
    return render(request, 'auctions/create_listing.html')

def index(request):
    auctions = AuctionListing.objects.all()
    sold_auctions = auctions.filter(sold = True)
    auctions = auctions.filter(sold = False)
    return render(request, "auctions/index.html", {
        "auctions": auctions,
        'sold_auctions': sold_auctions
    })


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")
