from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views import generic
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login
from .models import Group, Video
from .forms import VideoForm, SearchForm
from django.http import Http404, JsonResponse
from django.forms.utils import ErrorList
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
import urllib
import requests



YOUTUBE_API_KEY = 'AIzaSyDotkkcHwH7NSA1reRB9P4wDyMCLQAk1-0'

def home(request):
    recent_groups = Group.objects.all().order_by('-id')[:3]
    popular_groups = [Group.objects.get(pk=1),Group.objects.get(pk=2),Group.objects.get(pk=3)]
    return render(request, 'groups/home.html', {'recent_groups':recent_groups, 'popular_groups':popular_groups})

@login_required
def dashboard(request):
    groups = Group.objects.filter(user=request.user)
    return render(request, 'groups/dashboard.html', {'groups':groups})

@login_required
def add_video(request, pk):
    form = VideoForm()
    search_form = SearchForm()
    group = Group.objects.get(pk=pk)
    if not group.user == request.user:
        raise Http404
    if request.method == 'POST':
        form = VideoForm(request.POST)
        if form.is_valid():
            video = Video()
            video.group = group
            video.url = form.cleaned_data['url']
            parsed_url = urllib.parse.urlparse(video.url)
            video_id = urllib.parse.parse_qs(parsed_url.query).get('v')
            if video_id:
                video.youtube_id = video_id[0]
                response = requests.get(f'https://www.googleapis.com/youtube/v3/videos?part=snippet&id={ video_id[0] }&key={ YOUTUBE_API_KEY }')
                json = response.json()
                title = json['items'][0]['snippet']['title']
                video.title = title
                video.save()
                return redirect('detail_group', pk)
            else:
                errors = form._errors.setdefault('url', ErrorList())
                errors.append('Needs to be a YouTube URL')

    return render(request, 'groups/add_video.html', {'form':form, 'search_form':search_form, 'group':group})

@login_required
def video_search(request):
    search_form = SearchForm(request.GET)
    if search_form.is_valid():
        encoded_search_term = urllib.parse.quote(search_form.cleaned_data['search_term'])
        response = requests.get(f'https://www.googleapis.com/youtube/v3/search?part=snippet&maxResults=6&q={ encoded_search_term }&key={ YOUTUBE_API_KEY }')
        return JsonResponse(response.json())
    return JsonResponse({'error':'Not able to validate form'})

class DeleteVideo(LoginRequiredMixin, generic.DeleteView):
    model = Video
    template_name = 'groups/delete_video.html'
    success_url = reverse_lazy('dashboard')

    def get_object(self):
        video = super(DeleteVideo, self).get_object()
        if not video.group.user == self.request.user:
            raise Http404
        return video

class SignUp(generic.CreateView):
    form_class = UserCreationForm
    success_url = reverse_lazy('dashboard')
    template_name = 'registration/signup.html'

    def form_valid(self, form):
        view = super(SignUp, self).form_valid(form)
        username, password = form.cleaned_data.get('username'), form.cleaned_data.get('password1')
        user = authenticate(username=username, password=password)
        login(self.request, user)
        return view

class CreateGroup(LoginRequiredMixin, generic.CreateView):
    model = Group
    fields = ['title']
    template_name = 'groups/create_group.html'
    success_url = reverse_lazy('dashboard')

    def form_valid(self, form):
        form.instance.user = self.request.user
        super(CreateGroup, self).form_valid(form)
        return redirect('dashboard')

class DetailGroup(generic.DetailView):
    model = Group
    template_name = 'groups/detail_group.html'

class UpdateGroup(LoginRequiredMixin, generic.UpdateView):
    model = Group
    template_name = 'groups/update_group.html'
    fields = ['title']
    success_url = reverse_lazy('dashboard')

    def get_object(self):
        group = super(UpdateGroup, self).get_object()
        if not group.user == self.request.user:
            raise Http404
        return group

class DeleteGroup(LoginRequiredMixin, generic.DeleteView):
    model = Group
    template_name = 'groups/delete_group.html'
    success_url = reverse_lazy('dashboard')

    def get_object(self):
        group = super(DeleteGroup, self).get_object()
        if not group.user == self.request.user:
            raise Http404
        return group
