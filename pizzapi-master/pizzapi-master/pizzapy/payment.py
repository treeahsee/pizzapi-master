import re
import json


class CreditCard(object):
    """A CreditCard represents a credit card.

    There's some sweet logic in here to make sure that the type of card
    you passed is valid. 
    """
    def __init__(self, number='', card_expiry='', cvv='', zip=''):
        self.name = ''
        self.number = str(number).strip()
        self.card_type = self.find_type()
        self.card_expiry = str(card_expiry).strip()
        self.cvv = str(cvv).strip()
        self.zip = str(zip).strip()
        #if not self.validate():
            #raise Exception("Invalid Card.")

    def __repr__(self):
        return "Credit Card with last four #{}".format(self.number[-4:])

    def saveCC(self):
        filename = "card/CreditCard.json"
        json_dict = {"number": self.number,
             "card_expiry": self.card_expiry,
             "cvv": self.cvv,
             "zip": self.zip}

        with open(filename, "w") as f:
            json.dump(json_dict, f)

    @staticmethod
    def load(filename):
        """
        load and return a new customer object from a json file
        """
        with open(filename, "r") as f:
            data = json.load(f)

            card = CreditCard(data["number"], 
                                data["card_expiry"],
                                data["cvv"],
                                data["zip"])
        return card

    #def validate(self):
        #is_valid = self.number.isdigit() and len(self.number) == 16 and self.card_type != "" and len(self.expiration) == 4 and self.expiration.isdigit()
        #is_valid &= len(self.cvv) == 3 and self.cvv.isdigit()
        #is_valid &= 5 <= len(self.zip) >= 6
        #return is_valid

    def validate(self):
        is_valid = self.number and self.card_type and self.card_expiry
        is_valid &= re.match(r'^[0-9]{3,4}$', self.cvv)
        is_valid &= re.match(r'^[0-9]{5}(?:-[0-9]{4})?$', self.zip)
        return is_valid


    def find_type(self):
        patterns = {'VISA': r'^4[0-9]{12}(?:[0-9]{3})?$',
                    'MASTERCARD': r'^5[1-5][0-9]{14}$',
                    'AMEX': r'^3[47][0-9]{13}$',
                    'DINERS': r'^3(?:0[0-5]|[68][0-9])[0-9]{11}$',
                    'DISCOVER': r'^6(?:011|5[0-9]{2})[0-9]{12}$',
                    'JCB': r'^(?:2131|1800|35\d{3})\d{11}$',
                    'ENROUTE': r'^(?:2014|2149)\d{11}$'}
        return next((card_type for card_type, pattern in list(patterns.items())
                     if re.match(pattern, self.number)), '')
