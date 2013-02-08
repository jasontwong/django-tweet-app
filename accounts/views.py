from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login

def login_user(request):
    state = "Please log in below..."
    username = password = ''
    if request.POST:
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(username=username, password=password)
        if user != None:
            if user.is_active:
                login(request, user)
                state = "You're successfully logged in!"
                return redirect('/tweet_app/')
            else:
                state = "Your account is not active, please contact the site admin."
        else:
            state = "Your username and/or password were incorrect."

    data = {'state':state, 'username': username}
    return render(request, 'accounts/auth.html', data)
