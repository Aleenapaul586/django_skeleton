from django.shortcuts import render, get_object_or_404
from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from .models import Book, Author, BookInstance, Genre

def index(request):
    """View function for home page of site."""
    
    # Generate counts of some of the main objects
    num_books = Book.objects.count()
    num_instances = BookInstance.objects.count()

    # Available books (status = 'a')
    num_instances_available = BookInstance.objects.filter(status__exact='a').count()

    # The 'all()' is implied by default.
    num_authors = Author.objects.count()

    # Number of visits to this view, as counted in the session variable.
    num_visits = request.session.get('num_visits', 0)
    num_visits += 1
    request.session['num_visits'] = num_visits

    context = {
        'num_books': num_books,
        'num_instances': num_instances,
        'num_instances_available': num_instances_available,
        'num_authors': num_authors,
        'num_visits': num_visits,
    }

    # Render the HTML template index.html with the data in the context variable
    return render(request, 'catalog/index.html', context=context)

class BookListView(generic.ListView):
    model = Book
    paginate_by = 5  # Increased pagination for better navigation
    context_object_name = 'book_list'  # Your own name for the list as a template variable
    queryset = Book.objects.all()  # Get all books
    template_name = 'catalog/book_list.html'  # Specify your own template name/location

class BookDetailView(LoginRequiredMixin, generic.DetailView):
    """View to show details of a specific book, restricted to logged-in users."""
    model = Book
    template_name = 'catalog/book_detail.html'  # Ensure this template exists

class AuthorListView(generic.ListView):
    model = Author
    template_name = "catalog/author_list.html"
    context_object_name = "author_list"

class AuthorDetailView(LoginRequiredMixin, generic.DetailView):
    """View to show details of a specific author, restricted to logged-in users."""
    model = Author
    template_name = 'catalog/author_detail.html' 

class LoanedBooksByUserListView(LoginRequiredMixin, generic.ListView):
    """Generic class-based view listing books on loan to current user."""
    model = BookInstance
    template_name = 'catalog/bookinstance_list_borrowed_user.html'
    paginate_by = 10

    def get_queryset(self):
        """Filter to show only books loaned by the currently logged-in user."""
        return (
            BookInstance.objects.filter(borrower=self.request.user)
            .filter(status__exact='o')
            .order_by('due_back')
        )

class BorrowedBooksListView(LoginRequiredMixin, PermissionRequiredMixin, generic.ListView):
    """View listing all borrowed books. Admins see all, users see their own."""
    model = BookInstance
    template_name = 'catalog/borrowed_books.html'
    context_object_name = 'borrowed_books'
    permission_required = 'catalog.view_bookinstance'
    paginate_by = 10

    def get_queryset(self):
        """Return borrowed books. Staff sees all, regular users see only their own."""
        queryset = BookInstance.objects.filter(status='o').select_related('book', 'borrower').order_by('due_back')
        if not self.request.user.is_staff:
            queryset = queryset.filter(borrower=self.request.user)
        return queryset