from datetime import datetime
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q
# from django.views.generic import ListView, DetailView, UpdateView, CreateView, DeleteView
from django.views import generic
from .models import Post, Comment, Category, PostCategory, Author
from .filters import PostFilter
from .forms import PostForm, CommentForm


class NewsList(generic.ListView):
    """ Вывод из базы данных всех постов. Так же сортировка по дате, от самой свежей новости до старой
    с помощью ordering = ['-create_date'].
    paginate_by - позволяет выводить указанное количество постов на страницу """
    model = Post
    context_object_name = "post_list"
    ordering = ['-create_date']
    paginate_by = 5

    """ get_context_data() - Этот метод используется для заполнения словаря для использования в качестве контекста 
    шаблона. Например, ListViews заполнит результат из get_queryset() как object_list. Вероятно, вы будете чаще 
    всего переопределять этот метод, чтобы добавлять объекты для отображения в ваших шаблонах. """

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['time_now'] = datetime.now()
        context['category_name'] = Category.objects.all()
        context['filter'] = PostFilter(self.request.GET, queryset=self.get_queryset())
        return context


class NewsDetail(generic.edit.FormMixin, generic.DetailView):
    """ Выводим полностью все данные поста: заголовок поста, дату его создания, сам текст поста, автора поста,
    рейтинги поста и автора. Так же тут видим и комментарии к этому посту, автора комментария и рейтинг комментария. """
    model = Post
    context_object_name = 'post_detail'
    form_class = CommentForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['time_now'] = datetime.now()
        context['comment_list'] = Comment.objects.filter(comment_post=self.kwargs['pk'])
        context['post_category'] = PostCategory.objects.get(post=self.kwargs['pk']).category
        context['form'] = self.get_form()
        return context


class CategoryDetail(generic.DetailView):
    """ Выводим список категорий. Далее фильтруем посты по категориям и делаем вывод всех постов
    относящихся к данной категории. """
    model = Category
    context_object_name = 'category_detail'

    def get_context_data(self, **kwargs):
        id = self.kwargs.get('pk')
        context = super().get_context_data(**kwargs)
        " Контекст для списка постов в текущей категории. "
        context['category_news'] = Post.objects.filter(post_category=id)
        " Контекст постов данной категории. "
        context['post_category'] = PostCategory.objects.get(post=self.kwargs['pk']).category
        return context


class SearchListViews(NewsList):
    """ Модель создания страницы поиска постов по созданному фильтру в файле filters.py с помощью django_filters.
     Создаем фильтр модель и забираем отфильтрованные объекты переопределяя метод get_context_data
     у наследуемого класса (привет, полиморфизм, мы скучали!!!)
    """
    model = Post
    template_name = 'search_list.html'
    context_object_name = 'search'  # имя списка

    # def get_queryset(self):
    #     if self.request.GET.get('q_headline') and self.request.GET.get('q_author') and self.request.GET.get('q_date'):
    #         text = self.request.GET.get('q_headline')
    #         author = self.request.GET.get('q_author')
    #         date = self.request.GET.get('q_date')
    #         post_list = Post.objects.filter(Q(header=text) & Q(author_name=author) & Q(date_field__gte=date))
    #         return post_list

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['time_now'] = datetime.now()
        context['filter'] = PostFilter(self.request.GET, queryset=self.get_queryset())
        return context


# =============== Создаем классы UpdateView - обновление, CreateView - создание, DeleteView - удаление ===============
class PostCreateView(generic.CreateView):
    """ С помощью данного класса будет создавать посты взаимодействую с веб интерфейсом """
    model = Post
    # template_name = 'post_create.html'
    form_class = PostForm

    # Функция для кастомной валидации полей формы модели
    def form_valid(self, form):
        # создаем форму, но не отправляем его в БД, пока просто держим в памяти
        fields = form.save(commit=False)
        # Через реквест передаем недостающую форму, которая обязательно
        # fields.post_author = Author.objects.get(author_user=self.request.user)
        # Наконец сохраняем в БД
        fields.save()
        return super().form_valid(form)

    # def get_context_data(self, **kwargs):
    #     context = super().get_context_data(**kwargs)
    #     # context['is_not_author'] = not self.request.user.groups.filter(name='authors').exists()
    #     context['time_now'] = datetime.now()
    #     return context


class PostUpdateView(generic.UpdateView):
    """ С помощью данного класса мы будем редактировать посты взаимодействую с веб интерфейсом """
    form_class = PostForm
    template_name = 'post_update.html'

    # метод get_object чтобы получить информацию об объекте который мы собираемся редактировать
    def get_object(self, **kwargs):
        id = self.kwargs.get('pk')
        return Post.objects.get(pk=id)

    # def get_context_data(self, **kwargs):
    #     context = super().get_context_data(**kwargs)
    #     # context['is_not_author'] = not self.request.user.groups.filter(name='authors').exists()
    #     context['time_now'] = datetime.now()
    #     return context


class PostDeleteView(generic.DeleteView):
    """ Класс с помощью, которого можно удалять посты взаимодействую с веб интерфейсом """
    queryset = Post.objects.all()
    # permission_required = 'news.delete_post'
    success_url = '/news'

    # def get_context_data(self, **kwargs):
    #     context = super().get_context_data(**kwargs)
    #     context['is_not_author'] = not self.request.user.groups.filter(name='authors').exists()
    #     context['time_now'] = datetime.now()
    #     return context

# ================= Завершение создания классов UpdateView, CreateView, DeleteView ====================

# ============= Реализация повышения рейтинга =================================
# def add_like(request):
#     if request.POST:
#         pk = request.POST.get('pk')
#         post = Post.objects.get(id=pk)
#         post.like()
#         # post.postAuthor.update_rating()
#     return redirect(request.META.get('HTTP_REFERER'))


# @login_required
def add_like(request):
    if request.POST:
        pk = request.POST.get('pk')
        post = Post.objects.get(pk=pk)
        post.like()
        # post.postAuthor.update_rating()
    return redirect(request.META.get('HTTP_REFERER'))
