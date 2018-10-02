from django.shortcuts import render,get_object_or_404,redirect
from django.utils import timezone
from blog.models import Post, Comment
from blog.forms import PostForm, CommentForm,SignUpForm
from django.urls import reverse_lazy
from django.contrib import messages
from django.http import HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import (TemplateView, ListView,
                                    DetailView,CreateView,
                                    UpdateView,DeleteView)
# Class Based Views Here

class AboutView(TemplateView):
	template_name = 'about.html'

class PostListView(ListView):
	model = Post

	def get_queryset(self):
		return Post.objects.filter(published_date__lte=timezone.now()).order_by('-published_date')

class PostDetailView(DetailView):
	model = Post

class CreatePostView(LoginRequiredMixin,CreateView):
	login_url = '/login/'
	redirect_field_name = 'blog/post_detail.html'
	form_class = PostForm
	model = Post

class PostUpdateView(LoginRequiredMixin,UpdateView):
	login_url = '/login/'
	redirect_field_name = 'blog/post_detail.html'
	form_class = PostForm
	model = Post

class PostDeleteView(LoginRequiredMixin,DeleteView):
	model = Post
	success_url = reverse_lazy('post_list')

class DraftListView(LoginRequiredMixin,ListView):
	login_url = '/login/'
	redirect_field_name = 'blog/post_list.html'
	model = Post

	def get_queryset(self):
		return Post.objects.filter(published_date__isnull=True).order_by('created_date')


###########################
###########################
#Function Based Views Here

@login_required
def post_publish(request,pk):
	post = get_object_or_404(Post, pk=pk)
	post.publish()
	return redirect('post_detail',pk=pk)

@login_required
def add_comment_to_post(request,pk):
	post = get_object_or_404(Post,pk=pk)
	if request.method == 'POST':
		form = CommentForm(request.POST)
		if form.is_valid():
			comment = form.save(commit=False)
			comment.post = post
			comment.save()
			return redirect('post_detail',pk=post.pk)
	else:
		form = CommentForm()
	return render(request,'blog/comment_form.html',{'form':form})

@login_required
def comment_approve(request,pk):
	comment = get_object_or_404(Comment,pk=pk)
	comment.comment_approve()
	return redirect('post_detail',pk=comment.post.pk)

@login_required
def comment_remove(request,pk):
	comment = get_object_or_404(Comment,pk=pk)
	post_pk = comment.post.pk
	comment.delete()
	return redirect('post_detail',pk=post_pk)
def login_user(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
           # messages.success(request, 'You Have Logged In !!!')
            return redirect('post_list')

        else:
            return redirect('login_user')
    else:
        return render(request, 'login_user.html', {})


def logout_user(request):
    logout(request)
    messages.success(request, 'You Have Been Logged Out')
    return redirect('post_list')


def register_user(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data['username']
            password = form.cleaned_data['password1']
            user = authenticate(username=username, password=password)
            login(request, user)
            #messages.success(request, 'You Have Registered !!!')
            return redirect('post_list')

    else:
        form = SignUpForm()

    context = {'form': form}
    return render(request, 'register.html', context)

