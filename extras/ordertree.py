import sys
from bintrees import FastRBTree
from decimal import Decimal

# SCRIPT COMPLETAMENTE CREADO POR BITSO ---------

class OrderTree(object):
    def __init__(self):
        self.price_tree = FastRBTree()
        self.min_price = None
        self.max_price = None

    def get_orders_at_price(self, price):
        return self.price_tree.get(price)

        
    def insert_price(self, price, amount, oid):
        ## ignore market order
        if price == Decimal(0.0):            
            return
        prev_val = self.get_orders_at_price(price)
        if prev_val != None:
            ## price exists in local order book
            if oid in prev_val:
                ## update to an existing order at price
                prev_val['total'] = prev_val['total'] - prev_val[oid] + amount
                prev_val[oid] = amount
            else:
                ## new order at price
                prev_val['total'] += amount
                prev_val[oid] = amount
            self.price_tree.insert(price, prev_val)
        elif amount != 0.0:
            ## price did not exit in order book
            val = {'total': amount, oid: amount}
            self.price_tree.insert(price, val)

        try:
            val = self.price_tree.get(price)
            if val['total'] > 0:
                if self.max_price == None or price > self.max_price:
                    self.max_price = price
                if self.min_price == None or price < self.min_price:
                    self.min_price = price
            elif val['total'] == 0:
                ## price removed from orderbook
                self.remove_price(price)
            else:
                ## something has gone terribly wrong
                pass
        except:
            pass
    def remove_price(self, price):
        self.price_tree.remove(price)
        if self.max_price == price:
            try:
                self.max_price = max(self.price_tree)
            except ValueError:
                self.max_price = None
        if self.min_price == price:
            try:
                self.min_price = min(self.price_tree)
            except ValueError:
                self.min_price = None