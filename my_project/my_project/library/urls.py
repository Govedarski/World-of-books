from django.urls import path

from my_project.library.views import ShowBooksDashboardView, CreateBookView, DetailsBookView, EditBookView, \
    DeleteBookView, receive_book_view, not_receive_book_view, ShowBookList

urlpatterns = [
    path('list/', ShowBookList.as_view(), name='book_list'),
    path('dashboard/mine', ShowBooksDashboardView.as_view(), name='show_books_dashboard'),
    path('add/', CreateBookView.as_view(), name='create_book'),
    path('details/<int:pk>/', DetailsBookView.as_view(), name='book_details'),
    path('edit/<int:pk>/', EditBookView.as_view(), name='edit_book'),
    path('delete/<int:pk>/', DeleteBookView.as_view(), name='delete_book'),

    path('receive/<int:pk>/', receive_book_view, name='receive_book'),
    path('not_receive/<int:pk>/', not_receive_book_view, name='not_receive_book'),
]
