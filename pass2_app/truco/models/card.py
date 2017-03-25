# -*- encoding: utf-8 -*-

from django.db import models


class Card(models.Model):
    number = models.PositiveIntegerField(default=0)
    palo = models.CharField(default='r', max_length=10)
    position = models.IntegerField(default=0) # la posicion es 0 = carta en mano, 1,2,3 = carta tirada en primer, segundo y tercer confrontamiento.
    anchor = models.IntegerField() # el ancla de la carta es su posición original en el abanico de cartas de la mano del player, solo para uso visual.

    jerarquia = {
        '1o':8,'2o':9,'3o':10,'4o':1,'5o':2,'6o':3,'7o':11,'10o':5,'11o':6,'12o':7,
        '1e':14,'2e':9,'3e':10,'4e':1,'5e':2,'6e':3,'7e':12,'10e':5,'11e':6,'12e':7,
        '1b':13,'2b':9,'3b':10,'4b':1,'5b':2,'6b':3,'7b':4,'10b':5,'11b':6,'12b':7,
        '1c':8,'2c':9,'3c':10,'4c':1,'5c':2,'6c':3,'7c':4,'10c':5,'11c':6,'12c':7,
    }

 
    @staticmethod
    def generate_mazo():
        new_mazo = []
        for card in Card.jerarquia.keys():
            new_mazo.append(
                (int(card[:-1]), card[-1:])
                )
        return new_mazo

    def set_from_tuple(self, the_tuple):
        self.number = the_tuple[0]
        self.palo = the_tuple[1]
        self.position = 0
        self.save()



    def en_mano(self):
    	return self.position == 0

    def to_string(self):
        return '%d%s' % (self.number, self.palo)

    def get_score(self):
    	return self.jerarquia[self.to_string()]
    
    def get_css_class(self):
    	if self.position == 1:
    	    res = 'firstCard'
    	elif self.position == 2:
    	    res = 'secondCard'
    	else:
    	    res = 'thirdCard'
    	    
    	return res


    def __unicode__(self):
        return '%d%s' % (self.number, self.palo)
    
    class Meta:
        app_label = 'truco'
