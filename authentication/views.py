from django.shortcuts import render , redirect
from django.http import HttpResponse , JsonResponse
from database.db import db
from database.collections import *
from adminPanel.support import login_required , admin_required
from datetime import datetime
from bson import ObjectId

# Create your views here.
def loginFunc(req):
    if "user_id" in req.session:
        return redirect(homeFunc)
     
    if req.method == "POST":
        email = req.POST.get("email")
        password = req.POST.get("password")

        user = users.find_one({"email" : email , "password" : password})
        if user:
            req.session["user_id"] = str(user["_id"])
            req.session["user_name"] = user["name"]
            req.session["user_email"] = user["email"]
            req.session["user_status"] = user["status"]
            
            return JsonResponse({
                "status" : True,
                "message" : "Login Successfull",
                "user_status" : req.session["user_status"]
            })
        
        return JsonResponse({
            "status": False,
            "message": "Invalid Email or Password"
        })

    return render(req , "admin/login.html")

def signupFunc(req):
    if "user_id" in req.session:
        return redirect(homeFunc)
        
    if req.method == "POST":
        name = req.POST.get("name")
        email = req.POST.get("email")
        phone = req.POST.get("phone")
        password = req.POST.get("password")
        status = False

        customer = {"name" : name , "email" : email , "phone" : phone , "password" : password , "status" : status}
        result = users.insert_one(customer)

        if result.acknowledged:
            return JsonResponse({
                "status": True,
                "message": "User Registered Successfully"
            })

        return JsonResponse({
            "status": False,
            "message": "Unable to Register User"
        })
        

    return render(req , "admin/signup.html")

@login_required
def logoutFunc(req):
    if "user_id" not in req.session:
        return redirect(loginFunc)

    req.session.flush()
    return redirect(loginFunc)


@login_required
@admin_required
def homeFunc(req):

    if "user_id" not in req.session:
        return redirect(loginFunc)

    # --------------------------------
    # 1. Dashboard Statistics
    # --------------------------------

    total_movies = movie.count_documents({})
    total_bookings = booking.count_documents({})
    total_users = users.count_documents({})
    total_theaters = theater.count_documents({})

    # --------------------------------
    # 2. Booking Status Statistics
    # --------------------------------

    confirmed_bookings = booking.count_documents({
        "status": {"$in": ["confirm", "confirmed"]}
    })

    cancelled_bookings = booking.count_documents({
        "status": {"$in": ["cancel", "cancelled"]}
    })

    pending_bookings = total_bookings - (
        confirmed_bookings + cancelled_bookings
    )

    if total_bookings > 0:

        confirmed_percentage = round(
            confirmed_bookings / total_bookings * 100
        )

        cancelled_percentage = round(
            cancelled_bookings / total_bookings * 100
        )

        pending_percentage = round(
            pending_bookings / total_bookings * 100
        )

    else:
        confirmed_percentage = 0
        cancelled_percentage = 0
        pending_percentage = 0

    # --------------------------------
    # 3. Monthly Booking Analytics
    # --------------------------------

    current_year = datetime.now().year

    monthly_bookings = [0] * 12

    all_year_bookings = booking.find({
        "booking_date": {
            "$gte": datetime(current_year, 1, 1),
            "$lt": datetime(current_year + 1, 1, 1)
        }
    })

    for b in all_year_bookings:

        booking_date = b.get("booking_date")

        if booking_date:
            monthly_bookings[booking_date.month - 1] += 1

    # --------------------------------
    # 4. Recent Bookings
    # --------------------------------

    recent_booking_docs = booking.find().sort(
        "booking_date", -1
    ).limit(5)

    recent_bookings = []

    for b in recent_booking_docs:

        # Get User Details
        user_obj = users.find_one({
            "_id": b.get("user_id")
        })

        # Get Show Details
        show_obj = shows.find_one({
            "_id": b.get("show_id")
        })

        # Get Movie Details
        movie_obj = None

        if show_obj:
            movie_obj = movie.find_one({
                "_id": show_obj.get("movie_id")
            })

        recent_bookings.append({

            "booking_id": str(b["_id"])[-8:],

            "user_name": (
                user_obj.get("name", "Unknown User")
                if user_obj else "Unknown User"
            ),

            "movie_name": (
                movie_obj.get("name", "Unknown Movie")
                if movie_obj else "Unknown Movie"
            ),

            "total_amount_gst": b.get("total_amount_gst", 0),

            "status": b.get("status", "pending")

        })

    # --------------------------------
    # 5. Dashboard Context
    # --------------------------------

    context = {

        "total_movies": total_movies,
        "total_bookings": total_bookings,
        "total_users": total_users,
        "total_theaters": total_theaters,

        "confirmed_bookings": confirmed_bookings,
        "cancelled_bookings": cancelled_bookings,
        "pending_bookings": pending_bookings,

        "confirmed_percentage": confirmed_percentage,
        "cancelled_percentage": cancelled_percentage,
        "pending_percentage": pending_percentage,

        "monthly_bookings": monthly_bookings,

        "recent_bookings": recent_bookings,

        "current_date": datetime.now().strftime("%d %B %Y")

    }

    return render(req, "admin/home.html", context)
