# _*_ coding: utf-8 _*_

"""
Created on Jul 14, 2017

@author: Lasha Gogua
"""

from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^success/$', views.SuccessView.as_view(), name='success'),
    url(r'^fail/$', views.FailView.as_view(), name='fail'),
    url(r'^generate-transaction/$', views.GenerateTransactionIdView.as_view(), name='generate_transaction'),
]
