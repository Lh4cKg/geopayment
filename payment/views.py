# _*_ coding: utf-8 _*_

"""
Created on Jul 14, 2017

@author: Lasha Gogua
"""

import logging
from django.http import HttpResponse, Http404
from django.shortcuts import render
from django.views import generic

# import payment module
from payment.tbc import *
from payment.utils import get_client_ip


logger = logging.getLogger(__name__)


class SuccessView(generic.DetailView):
    """
    Displays the 'thank you' page which summarises the order just submitted.
    """
    template_name = 'payment/thank_you.html'
    context_object_name = 'obj'

    # here some logic

    def get_context_data(self, **kwargs):
        ctx = super(SuccessView, self).get_context_data(**kwargs)

        return ctx


class FailView(generic.View):
    """
    Displays the 'fail' page which summarises the order not submitted.
    """

    def get(self, request, *args, **kwargs):
        return HttpResponse("<html>TBC Fail url</html>")


class GenerateTransactionIdView(generic.TemplateView):
    """
    generate transaction id
    """
    template_name = 'payment/transaction.html'

    def post(self, request, *args, **kwargs):
        ctx = {}
        amount = request.POST.get('amount')
        currency = request.POST.get('currency')
        client_ip_address = get_client_ip(request)
        result = generate_transaction_id(amount, currency, client_ip_address)

        ctx['amount'] = amount
        ctx['currency'] = currency
        ctx['client_ip'] = client_ip_address
        ctx['result'] = result
        ctx['trans_id'] = result.get('TRANSACTION_ID')
        return self.render_to_response(self.get_context_data(ctx=ctx))

    def get_context_data(self, **kwargs):
        ctx = super(GenerateTransactionIdView, self).get_context_data(**kwargs)
        ctx['label'] = 'enter amount'
        return ctx
