# _*_ coding: utf-8 _*_

"""
Created on Jul 14, 2017

@author: Lasha Gogua
"""

from django.conf import settings
from django.db import models


class Transaction(models.Model):
    transaction_id = models.CharField('Transaction Identifier', max_length=64, unique=True)
    status = models.CharField('Status', max_length=10)
    status_code = models.PositiveIntegerField('Status Code', default=0)
    amount = models.DecimalField('Amount', decimal_places=2, max_digits=12, null=True)
    currency = models.CharField('Currency', max_length=5)
    basket = models.BigIntegerField('Basket', null=True, blank=True)
    merchant = models.CharField('Merchant', max_length=250, null=True, blank=True)
    provider = models.CharField('Provider', max_length=500, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'payment_transactions'
        verbose_name = 'Transaction'
        verbose_name_plural = 'Transactions'

    def __str__(self):
        return 'Status: %s - Status Code: %s - Transaction ID: %s' % (self.status, self.status_code, self.transaction_id)
