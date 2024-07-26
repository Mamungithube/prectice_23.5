from django import forms
from .models import Transaction
from accounts.models import UserBankAccount
from django.contrib.auth.models import User
class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = [
            'amount',
            'transaction_type'
        ]

    def __init__(self, *args, **kwargs):
        self.account = kwargs.pop('account') 
        super().__init__(*args, **kwargs)
        self.fields['transaction_type'].disabled = True
        self.fields['transaction_type'].widget = forms.HiddenInput() 

    def save(self, commit=True):
        self.instance.account = self.account
        self.instance.balance_after_transaction = self.account.balance
        return super().save()

class DepositForm(TransactionForm):
    def clean_amount(self):
        min_diposit_amount = 100
        amount = self.cleaned_data.get('amount')
        if amount < min_diposit_amount:
            raise forms.validation_errors(
                f'Your amount is too low ,you amount must be between"{min_diposit_amount}'
            )
        return amount

from django import forms

class WithdrawForm(TransactionForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Assuming 'balance' is an attribute of the form instance
        self.balance = 1000  # Replace with the actual balance value

    def clean_amount(self):
        min_withdraw_amount = 100
        max_deposit_amount = 20000
        amount = self.cleaned_data.get('amount')

        if amount < min_withdraw_amount:
            raise forms.ValidationError(
                f"Your amount is too low, it must be between {min_withdraw_amount}."
            )
        if amount > max_deposit_amount:
            raise forms.ValidationError(
                f"Your amount is too high, it must be between {max_deposit_amount}."
            )
        if amount > self.balance:
            raise forms.ValidationError(
                f"Your balance is not enough, it must be less than {self.balance}."
            )

        return amount

    
class LoanRequestForm(TransactionForm):
    def clean_amount(self):
        amount = self.cleaned_data['amount']
        return amount
    
class TransferForm(forms.Form):
    recipient = forms.ModelChoiceField(queryset=User.objects.all())
    amount = forms.DecimalField(max_digits=12,decimal_places=2)

    def __init__(self,*args,**kwargs):
        self.sender_account = kwargs.pop('account')
        super().__init__(*args,**kwargs)

    def clean_amount(self):
        amount = self.cleaned_data.get('amount')
        if self.sender_account.balance < amount:
            raise forms.ValidationError('Insufficient balance')
        return amount
    
    def clean_recipient(self):
        recipient = self.cleaned_data.get('recipient')
        try:
            recipient_account = recipient.account
        except UserBankAccount.DoesNotExist:
            raise forms.ValidationError('Recipient does not have a bank account')
        return recipient
    
    def save(self,commit=True):
        recipient = self.cleaned_data.get('recipient')
        amount = self.cleaned_data.get('amount')

        sender_account = self.sender_account
        recipient_account = recipient.account

        sender_account.balance  -= amount
        recipient_account.balance  += amount

        sender_account.save(update_fields =['balance'])
        recipient_account.save(update_fields =['balance'])