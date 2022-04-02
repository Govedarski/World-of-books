from django.urls import path

from my_project.offer.views import CreateOfferView, ShowOfferDetailsView, accept_offer_view, decline_offer_view, \
    NegotiateOfferView, ShowOfferView

urlpatterns = [
    path('create/<int:pk>/', CreateOfferView.as_view(), name='create_offer'),
    path('details/<int:pk>/', ShowOfferDetailsView.as_view(), name='show_offer_details'),
    path('dashboard/', ShowOfferView.as_view(), name='show_offer_list'),

    path('accept/<int:pk>/', accept_offer_view, name='accept_offer'),
    path('decline/<int:pk>/', decline_offer_view, name='decline_offer'),
    path('negotiate/<int:pk>/', NegotiateOfferView.as_view(), name='negotiate_offer'),
]
