from django.urls import reverse_lazy, reverse
from pytils.translit import slugify
from django.views.generic import CreateView, ListView, DetailView, UpdateView, DeleteView

from notebook.models import Blog


class BlogCreateView(CreateView):
    model = Blog
    fields = ('blog_title', 'blog_text',)
    success_url = reverse_lazy('notebook:list')

    def form_valid(self, form):
        if form.is_valid():
            new_blog = form.save()
            new_blog.blog_slug = slugify(new_blog.blog_title)
            new_blog.save()
        return super().form_valid(form)
class BlogListView(ListView):
    model = Blog

    def get_queryset(self, *args, **kwargs):
        queryset = super().get_queryset()
        queryset = queryset.filter(blog_is_active=True)
        return queryset


class BlogDetailView(DetailView):
    model = Blog

    def get_object(self, queryset=None):
        self.object = super().get_object(queryset)
        self.object.blog_count += 1
        self.object.save()
        return self.object

class BlogUpdateView(UpdateView):
    model = Blog
    fields = ('blog_title', 'blog_text',)
    # success_url = reverse_lazy('notebook:list')

    def form_valid(self, form):
        if form.is_valid():
            new_blog = form.save()
            new_blog.blog_slug = slugify(new_blog.blog_title)
            new_blog.save()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('notebook:view', args=[self.kwargs.get('pk')])

class BlogDeleteView(DeleteView):
    model = Blog
    success_url = reverse_lazy('notebook:list')