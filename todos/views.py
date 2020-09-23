from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.contrib.auth import login, logout, authenticate
from .forms import TodoForm
from .models import Todo
from django.utils import timezone
from django.contrib.auth.decorators import login_required

# HOME
def home(request):
    if request.method == 'GET':
        return render(request, 'todos/home.html', {'form':AuthenticationForm()} )
    else:
        user = authenticate(request, username=request.POST['username'], password=request.POST['password'])
        if user is None:
            return render(request, 'todos/home.html', {'form':AuthenticationForm(), 'error':'Username and Password did not match'})
        else:
            login(request, user)
            return redirect('currenttodo')
    

#LOG_IN_FORM
# def userlogin(request):
#     if request.method == 'GET':
#         return render(request, 'todos/login.html', {'form':AuthenticationForm()} )
#     else:
#         user = authenticate(request, username=request.POST['username'], password=request.POST['password'])
#         if user is None:
#             return render(request, 'todos/login.html', {'form':AuthenticationForm(), 'error':'Username and Password did not match'})
#         else:
#             login(request, user)
#             return redirect('currenttodo')
        
#SIGN_UP_FORM
def usersignup(request):
    if request.method == 'GET':
        return render(request, 'todos/signup.html', {'form':UserCreationForm()} )
    else:
        if request.POST['password1'] == request.POST['password2']:
            try:
                user = User.objects.create_user(request.POST['username'], password = request.POST['password1'])
                user.save()
                login(request, user)
                return redirect('currenttodo')
            except IntegrityError:
                return render(request, 'todos/signup.html', {'form':UserCreationForm(), 'error':'Username already taken. Choose another one'} )

        else:
            return render(request, 'todos/signup.html', {'form':UserCreationForm(), 'error':'Password did not match'} )

#LOG_OUT_FORM
@login_required
def userlogout(request):
    if request.method == 'POST':
        logout(request)
        return redirect('home')

#Creating todos
@login_required
def createtodo(request):
    if request.method == 'GET':
        return render(request, 'todos/creations.html',{'form':TodoForm()})
    else:
        try:
            form = TodoForm(request.POST)
            newtodo = form.save(commit=False)
            newtodo.user = request.user
            newtodo.save()
            return redirect('currenttodo')
        except ValueError:
            return render(request, 'todos/creations.html',{'form':TodoForm() ,'error':'BAD DATA MF!!'})

#MAIN_TODO_PAGE
@login_required
def currenttodo(request):
    todos = Todo.objects.filter(user=request.user, date_done__isnull=True)
    return render(request, 'todos/currenttodo.html',{'todos':todos})

#Display completed todos
@login_required
def completedtodos(request):
    todos = Todo.objects.filter(user=request.user, date_done__isnull=False)
    return render(request, 'todos/completedtodos.html',{'todos':todos})


#viwing the todo list
@login_required
def viewtodo(request, todo_pk):
    todo = get_object_or_404(Todo, pk=todo_pk, user=request.user)
    if request.method == 'GET':
        form = TodoForm(instance=todo)
        return render(request, 'todos/viewtodo.html',{'todo':todo, 'form':form})
    else:
        try:
            form = TodoForm(request.POST, instance=todo)
            form.save()
            return redirect('currenttodo')
        except ValueError:
            return render(request, 'todos/viewtodo.html',{'todo':todo, 'form':form, 'error':'BAD DATA MF!!'})

#completing and removing todo
@login_required
def completetodo(request, todo_pk):
    todo = get_object_or_404(Todo, pk=todo_pk, user=request.user)
    if request.method == 'POST':
        todo.date_done = timezone.now()
        todo.save()
        return redirect('currenttodo')


@login_required
def deletetodo(request, todo_pk):
    todo = get_object_or_404(Todo, pk=todo_pk,user=request.user)
    if request.method == 'POST':
        todo.delete()
        return redirect('currenttodo')