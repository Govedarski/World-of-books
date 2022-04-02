from django.urls import path

from my_project.library.views import ShowBooksDashboardView, CreateBookView, DetailsBookView, EditBookView, \
    DeleteBookView, accept_delete_book_view, ShowBookListView, like_book_view, ShowBooksOnAWayView, \
    ShowBooksToSendView, reject_delete_book_view, receive_book_view

urlpatterns = [
    path('list/', ShowBookListView.as_view(), name='book_list'),
    path('dashboard/<int:pk>/', ShowBooksDashboardView.as_view(), name='show_books_dashboard'),
    path('on_a_way/', ShowBooksOnAWayView.as_view(), name='show_books_on_a_way'),
    path('to_send/', ShowBooksToSendView.as_view(), name='show_books_to_send'),
    path('add/', CreateBookView.as_view(), name='create_book'),
    path('details/<int:pk>/', DetailsBookView.as_view(), name='book_details'),
    path('edit/<int:pk>/', EditBookView.as_view(), name='edit_book'),
    path('delete/<int:pk>/', DeleteBookView.as_view(), name='delete_book'),
    path('like/<int:pk>/', like_book_view, name='like_book'),

    path('accept_deleted/<int:pk>/', accept_delete_book_view, name='accept_delete_book'),
    path('reject_deleted/<int:pk>/', reject_delete_book_view, name='reject_delete_book'),
    path('recieve/<int:pk>/', receive_book_view, name='receive_book'),
]
