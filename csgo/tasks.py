from csgo.messsage_wrapper import TransactionNotification
from .models import Transaction
from .logic.trade import TradeLogic

def auto_notification():
    txns = Transaction.objects.filter(state__in=[Transaction.PCM,Transaction.TST,Transaction.TAC],notification_sent=False)
    for txn in txns:
        notification = TransactionNotification(txn)
        notification.send_state_notification()
    txns.update(notification_sent=True)
    
#TODO: Improve performance by skipping the float detection for the items
def auto_trade_sent():
    txns = Transaction.objects.filter(state=Transaction.PCM)
    for txn in txns:
        trade = TradeLogic(txn)
        if trade.trade_sent():
            txn.state = Transaction.TST
            txn.save()

def auto_trade_accept():
    txns = Transaction.objects.filter(state=Transaction.TST)
    for txn in txns:
        trade = TradeLogic(txn)
        if trade.trade_accepted():
            txn.state = Transaction.TAC
            txn.save()