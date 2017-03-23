# -*- coding: utf-8 -*-
"""
Editor de Spyder

Este es un archivo temporal
"""

import sys
import asyncio
import random
import telepot
from telepot.aio.delegate import per_chat_id, create_open, pave_event_space

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

from nltk.metrics import edit_distance
from nltk import stem, tokenize

"""
$ python3.5 guessa.py <token>
Guess a number:
1. Send the bot anything to start a game.
2. The bot randomly picks an integer between 0-99.
3. You make a guess.
4. The bot tells you to go higher or lower.
5. Repeat step 3 and 4, until guess is correct.
"""

class Player(telepot.aio.helper.ChatHandler):

    def __init__(self, *args, **kwargs):
        super(Player, self).__init__(*args, **kwargs)
        self._answer = random.randint(0,99)
        self._status = 'EMPTY'
        self._st_cp = 0
        self._st_metric = ''
        self.stemmer = stem.PorterStemmer()

    def _hint(self, answer, guess):
        if answer > guess:
            return 'larger'
        else:
            return 'smaller'
 
    def _calc_command(self, command):
        list_available_options = ["VIAJ", "COMPR", "FIESTA", "BAR", "RESTAURANTE", ""]
        dictionary = dict.fromkeys(list_available_options, command)

        for key,value in dictionary.items() :
            self.fuzzy_match(key, value)
 
    def normalize(self, s):
        words = tokenize.wordpunct_tokenize(s.lower().strip())
        return ' '.join([self.stemmer.stem(w) for w in words])
     
    def fuzzy_match(self, s1, s2, max_dist=3):
        print("\n"+s1+" - "+s2+" : "+ str(edit_distance(self.normalize(s1), self.normalize(s2))))
        
    def _calculate_command(self, command):
        list_available_options = ["VIAJ", "COMPR", "FIESTA", "BAR", "RESTAURANTE", ""]
        
        print ("\nUser Introduces command "+command)
    
        #GENERATE A KV DICTIONARY TO MATCH ALL INPUT COMMANDS VS ALL AVAILABLE OPTIONS
        #WE WILL RETURN THE LEVENSHTEIN COEFFICIENTS FOR EACH INPUT COMMAND
        #WE CAN ITERATE DIRECTLY OVER THE TWO LISTS, BUT I WANTED TO SHOW THAT I CAN OPERATE WITH DICTIONARIES :)
        dictionary = dict.fromkeys(list_available_options, command)
        levencoeff_min=None
        minaction=''
        minsuggestion =''
        
        for key,value in dictionary.items() :
            
            list_coeffs = []

            leven_coeff = edit_distance(key, value, substitution_cost=1, transpositions=True)
            
            if (levencoeff_min is None):
                levencoeff_min = leven_coeff
                minaction = key
            
            #NOTICE SUBSTITIUTIONS COST. WE CAN ADD MORE PENALTY TO THE COEFFICIENT FOR A SECUENTIAL SUBSTITUTION
            #WE CAN EVEN ADD MORE PENALTY FOR TRANSPOSITION PAIRS (ab, ba)
            #YOU CAN JUST TUNE THE CALCULATIONS
            print ("-----------------------------------------------------")
            print ("levenshtein coefficient for "+key+" "+value+":"+str(leven_coeff))
            #WE CAN EVALUATE THE COEFFICIENT AND IF ITS VALUE IS LOWER THAN A THRESHOLD, 
            #WE CAN SUGGEST THE COMMAND AGAINST WE ARE COMPARING
            #OTHERWISE WE CAN JUST NOTIFY WE DIDNT UNDERSTOOD THE COMMAND
            #JUST ADJUST THE COEFFICIENT THRESHOLD
            
            print ("Simulated output follows for all pairs:")
            
            if leven_coeff == 0:
                print ("command recognized, exact match")            
            elif leven_coeff > 4:
                print ("command not recognized, please try again...")
            else: print ("command "+value+", not recognized, maybe you were referring to "+key+"?")
            
            if (leven_coeff < levencoeff_min):
                levencoeff_min = leven_coeff
                minaction = key
                
        print ("\nAction suggested for command "+command+" (the one with lesser coefficient) is:")
        #evaluate again to show minimal action
        if levencoeff_min == 0:
            print ("command recognized, exact match")            
        elif levencoeff_min > 4:
            print ("command "+command+" not recognized, please try again...")
        else: print ("command "+command+" not recognized, maybe you were referring to "+minaction+"?")

        return minaction
        
        
            
    def _make_plot_bbva(self, my_zipcode, my_column):
        my_column = my_column.upper()
        if my_column == 'IMPORTE':
            my_column = 'avg'
            title = 'Media de compras por categoría'
        elif my_column == 'TARJETAS':
            my_column = 'cards'
            title = 'Media de tarjetas utilizadas por categoría'
        elif my_column == 'MERCHANTS':
            my_column = 'merchants'
            title = 'Media de merchants por categoría'
        elif my_column == 'TRANSACCIONES':
            my_column = 'txs'
            title = 'Media de transacciones por categoría'
        else:
            title = 'ERROR'
        title = title + " para el CP " + str(my_zipcode)
        
        df = pd.read_csv('D:/D4S/BBVA/output/MadridZipcodes_Categories.csv', sep=';', index_col=False, header=0)
        df.drop(['date', 'Filtered to at 10:42:26'], axis=1, inplace=True)

        grouped = df.groupby(['zipcode', 'category'])
        df = df.groupby(['zipcode', 'category'])[my_column].mean().reset_index()

        df = df[df['category'] != 'filtered']
        df = df[df['zipcode'] == my_zipcode]
        df_cats = df['category']
        df_avgs = df[my_column]

        N = len(df_avgs)
        width = 0.5
        x = range(N)
        plt.bar(x, df_avgs, width, color="blue")
        plt.xticks(x, df_cats, rotation='vertical')
        plt.title(title)
        #plt.show()
        plt.savefig('D:/D4S/BBVA/output/ExampleMatPlotLib.png', bbox_inches='tight')
        plt.close()

        return 'D:/D4S/BBVA/output/ExampleMatPlotLib.png'

    def _make_plot_mob(self, my_zipcode):
        df_mov = pd.read_csv('D:/D4S/BBVA/output/MadridZipcodes_MobilityProfiling.csv', sep=';', index_col=False, header=0)
        df_mov = df_mov[np.isfinite(df_mov['home_cp'])]
        df_mov.home_cp = df_mov.home_cp.astype(int)
        df_mov.drop(['gender', 'age', 'segment'], axis=1, inplace=True)
        df_mov = df_mov[df_mov['home_cp'] >= 28000]
        df_mov = df_mov[df_mov['home_cp'] <= 28999]

        df_mov = df_mov.groupby(['destination', 'home_cp'])['n_people'].sum().reset_index()
        df_mov = df_mov[df_mov['destination'] == my_zipcode]
        df_mov = df_mov.sort_values(by=['n_people', 'home_cp'], ascending=[False, True])

        df_x = df_mov['home_cp'].head(n=10)
        df_y = df_mov['n_people'].head(n=10)
        
        N = len(df_y)
        width = 0.5
        x = range(N)
        plt.bar(x, df_y, width, color="blue")
        plt.xticks(x, df_x, rotation='vertical')
        title = " Top 10 de CPs por cantidad de personas que van al CP " + str(my_zipcode)
        plt.title(title)
        plt.savefig('D:/D4S/BBVA/output/ExampleMatPlotLib_Mob.png', bbox_inches='tight')
        plt.close()
        
        return 'D:/D4S/BBVA/output/ExampleMatPlotLib_Mob.png'

    async def open(self, initial_msg, seed):
        #await self.sender.sendMessage('Hola!\nPodemos hablar de cómo se gasta el dinero la gente en Madrid.\n¿De qué código postal te gustaría saber la media de importe de compras?')
        await self.sender.sendMessage('Hola!: http://www.google.es')
        return True  # prevent on_message() from being called on the initial message

    async def on_chat_message(self, msg):
        content_type, chat_type, chat_id = telepot.glance(msg)

        #self._calculate_command(msg['text'].upper())
        self._calc_command(msg['text'].upper())
        await self.sender.sendMessage('Prueba más...')
        return
        
		
        
        #with open('D:/D4S/BotBD4SG/images/like.png', "rb") as image_file:
            #await self.sender.sendPhoto(image_file)
            #return

        if content_type != 'text':
            await self.sender.sendMessage('No puedo interpretar audio, vídeo, etc.\nEnvíame sólo palabras, por favor.')
            return

        if msg['text'].upper() == 'MOVILIDAD':
            self._status = 'MOVILIDAD'
            if self._st_cp != 0:
                with open(self._make_plot_mob(self._st_cp), "rb") as image_file:
                    await self.sender.sendPhoto(image_file)
                    self.close()
                    return
            else:
                await self.sender.sendMessage('Primero necesito saber el CP que te interesa. Mejor volvamos a empezar')
                self.close()
                return

        if self._status == 'EMPTY':
            if msg['text'].upper() == 'NO':
                await self.sender.sendMessage('Hasta luego!')
                self.close()
                return
            else:
                try:
                   cp_int = int(msg['text'])
                except ValueError:
                    await self.sender.sendMessage('Necesito un código postal (5 cifras)\nPor ejemplo: 28001')
                    return
                if cp_int < 28000 or cp_int > 28999:
                    await self.sender.sendMessage('El CP tiene que ser de Madrid (28000-28999)')
                    return
    
                await self.sender.sendMessage('De qué métrica quieres saber la media (importe, tarjetas, merchants, transacciones)')
                self._status = 'CP'
                self._st_cp = cp_int
                self._st_metric = ''
                
                return
        
        elif self._status == 'CP' and self._st_cp != 0 and self._st_metric == '':
            if msg['text'].upper() == 'NO':
                await self.sender.sendMessage('Algún otro CP?')
                self._status = 'EMPTY'
                self._st_cp = 0
                self._st_metric = ''
            else:
                with open(self._make_plot_bbva(self._st_cp, msg['text']), "rb") as image_file:
                    await self.sender.sendPhoto(image_file)
                    self._st_metric = msg['text']
                    return

        elif self._status == 'CP' and self._st_cp != 0 and self._st_metric != '':
            await self.sender.sendMessage('Alguna otra métrica? (importe, tarjetas, merchants, transacciones)')
            self._st_metric = ''
            return


    async def on__idle(self, event):
        await self.sender.sendMessage('Hasta luego!')
        #await self.sender.sendMessage('Game expired. The answer is %d' % self._answer)
        self.close()


TOKEN = sys.argv[1]

bot = telepot.aio.DelegatorBot(TOKEN, [
    pave_event_space()(
        per_chat_id(), create_open, Player, timeout=30),
])

loop = asyncio.get_event_loop()
loop.create_task(bot.message_loop())
print('Listening ...')

loop.run_forever()
