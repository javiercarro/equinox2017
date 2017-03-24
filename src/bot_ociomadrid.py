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
from nltk import stem, tokenize, word_tokenize

import googlemaps as gm

#import PrettyTable

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
        self._status = 'NONE'
        self._st_scope = 'NONE'
        self._st_cp = 0
        self._st_cp_list = []

    def _hint(self, answer, guess):
        if answer > guess:
            return 'larger'
        else:
            return 'smaller'
 
    def _list_places(self, zipcode):

        # Guardamos la respuesta de la llamada a la API Geocoding
        geocode_result = gmaps.geocode(str(zipcode), region="es")

        # Guardamos latitud y longitud 
        lat = geocode_result[0]["geometry"]["location"]["lat"]
        lng = geocode_result[0]["geometry"]["location"]["lng"]

        # Nos quedamos con los lugares (places) cercanos a esa latitud y longitud
        places = gmaps.places('restaurante', location=[lat, lng], radius=100, language="es-ES")["results"]

        # Generamos un diccionario con los datos que nos interesan y luego un DataFrame a partir del diccionario
        d = {}
        for index, place in enumerate(places):
            try:
                url = gmaps.place(place["place_id"], language="es-ES")["result"]["url"] #Get the url
            except:
                url = "No URL from Google Places"
                
            try:
                name = place["name"]
            except:
                name = "No name from Google Places"
                
            try:
                rating = place["rating"]
            except:
                rating = None
                
            d[index] =  {"name": name,"rating": rating, "url": url}

        df = pd.DataFrame(d).transpose()

        # Sacamos el los 10 con mejor rating y los 10 con peor rating
        top5 = df.sort_values(by="rating", ascending=False, na_position="last").head(5).reset_index().drop("index", axis=1)
        last5 = df.sort_values(by="rating", ascending=True, na_position="first").head(5).reset_index().drop("index", axis=1)
 
        return top5
 
    def _extract_command(self, command):
        try:
            cp_int = int(command)
            if cp_int < 28000 or cp_int > 28999:
                print('El CP tiene que ser de Madrid.')
                return
            else:
                self._st_cp = cp_int
                return 'CP'
        except ValueError:
            print('No es un CP')

        list_available_options = ["CP", "VIAJ", "EXCURSIÓN", "CENAR", "COMER", "TOMAR", "TAPAS", "CUANTO", "CUÁNTO", "CUESTA", "PRECIO", "COSTE", "RESTAURANTE", "LOCAL", "SUGERIR", "SUGERENCIA", "PROPON", "PROPUESTA"]
        dictionary = dict.fromkeys(list_available_options, command)
        s_txt = 'UNKNOWN'
        score = 100
        for key,value in dictionary.items():
            print("\nIterate: "+key+" - "+value)
            s_val = self.iterate_distance(key, value)
            if s_val < score:
                score = s_val
                s_txt = key
        return s_txt
 
    def iterate_distance(self, key, sentence):
        words = sentence.upper().split()
        print(words)
        score = 100
        for txt in words:
            if len(txt) > 3:
                s_t = edit_distance(key, txt, substitution_cost = 1, transpositions = True)
                if s_t <= score:
                    score = s_t
                print("\n"+key+" - "+txt+" : "+ str(score))
        return score
 
    def normalize(self, s):
        self.stemmer = stem.PorterStemmer()
        words = tokenize.wordpunct_tokenize(s.upper().strip())
        return ' '.join([self.stemmer.stem(w) for w in words])
     
    def fuzzy_match(self, s1, s2, max_dist=3):
        score = edit_distance(self.normalize(s1), self.normalize(s2))
        print("\n"+s1+" - "+s2+" : "+ str(score))
        return score
        
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

    def _make_plot_bbva_avg(self, cp_list):
        df = pd.read_csv('D:/D4S/BBVA/output/MadridZipcodes_Categories.csv', sep=';', index_col=False, header=0)
        df.drop(['date', 'Filtered to at 10:42:26'], axis=1, inplace=True)

        zps = cp_list
        df_zps = pd.DataFrame()

        for zp in zps:
            df_temp = df.loc[df["zipcode"] == zp]
            df_zps = df_zps.append(df_temp)

        df_zps = df_zps.groupby(["zipcode", "category"]).mean().reset_index(level="category")
        df_avgs = df_zps.loc[df_zps["category"] == "es_barsandrestaurants"]["avg"].sort_values(ascending=False)
        index = df_avgs.index

        N = len(df_avgs)
        width = 0.5
        x = range(N)
        plt.bar(x, df_avgs, width, color="blue")
        plt.xticks(x, index, rotation='vertical')
        plt.title('CPs con más bares y restaurantes (precios medios)')
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

    def _make_plot_mob_most(self):
        df_mov = pd.read_csv('D:/D4S/BBVA/output/MadridZipcodes_MobilityProfiling.csv', sep=';', index_col=False, header=0)
        df_mov = df_mov[np.isfinite(df_mov['home_cp'])]
        df_mov.home_cp = df_mov.home_cp.astype(int)
        df_mov.drop(['gender', 'age', 'segment'], axis=1, inplace=True)
        df_mov = df_mov[df_mov['home_cp'] >= 28000]
        df_mov = df_mov[df_mov['home_cp'] <= 28999]

        df_mov = df_mov.groupby(['destination'])['n_people'].sum().reset_index()
        df_mov = df_mov.sort_values(by=['n_people', 'destination'], ascending=[False, True])

        df_x = df_mov['destination'].head(n=10)
        df_y = df_mov['n_people'].head(n=10)
        
        self._st_cp_list = df_x
        
        N = len(df_y)
        width = 0.5
        x = range(N)
        plt.bar(x, df_y, width, color="blue")
        plt.xticks(x, df_x, rotation='vertical')
        title = "Top 10 CPs más frecuentados para tu caso"
        plt.title(title)
        plt.savefig('D:/D4S/BBVA/output/ExampleMatPlotLib_Mob.png', bbox_inches='tight')
        plt.close()
        
        return 'D:/D4S/BBVA/output/ExampleMatPlotLib_Mob.png'
   
    
    def format_for_print2(self, df):    
        table = PrettyTable(list(df.columns))
        for row in df.itertuples():
            table.add_row(row[1:])
        return str(table)    
        
    async def open(self, initial_msg, seed):
        await self.sender.sendMessage('¡Hola!\nPuedo ayudarte en tu ocio\n¿En qué estás interesado?')
        return True  # prevent on_message() from being called on the initial message

    async def on_chat_message(self, msg):
        content_type, chat_type, chat_id = telepot.glance(msg)

        action = self._extract_command(msg['text'].upper())
        await self.sender.sendMessage('Detectado: '+action+'.')
        
        #["VIAJ", "COMPR", "FIESTA", "BAR", "RESTAURANTE", ""]
        #self._status = 'NONE'
        #self._st_scope = 'NONE'
        #self._st_cp = 0
        if action == 'VIAJ' or action == 'EXCURSIÓN':
            if self._status == 'NONE' and self._st_scope == 'NONE' and self._st_cp == 0:
                await self.sender.sendMessage('Mmmh, un viaje, suena bien.\n¿En qué quieres que te ayude?')
                self._status = 'VIAJE'
                return
            else:
                await self.sender.sendMessage('¿Puedes decírmelo de otra forma, por favor?')
                return
        elif action == 'CENAR' or action == 'COMER' or action == 'TOMAR' or action == 'TAPAS':
            with open(self._make_plot_mob_most(), "rb") as image_file:
                await self.sender.sendPhoto(image_file)
                self._st_scope = action
            return
        elif action == 'CUANTO' or action == 'CUÁNTO' or action == 'CUESTA' or action == 'PRECIO' or action == 'COSTE':
            if self._st_scope == 'CENAR' or self._st_scope == 'COMER' or self._st_scope == 'TOMAR' or self._st_scope == 'TAPAS':
                with open(self._make_plot_bbva_avg(self._st_cp_list), "rb") as image_file:
                    await self.sender.sendPhoto(image_file)
                    #self._st_scope = action
                return
            else:
                await self.sender.sendMessage('Lo siento, no tengo información de precios respecto a ese tema.')
                return
        elif action == 'RESTAURANTE' or action == 'GARITO' or action == 'BAR' or action == 'RESTAURANTE' or action == 'LOCAL' or action == 'SUGERIR' or action == 'SUGERENCIA' or action == 'PROPON' or action == 'PROPUESTA':
            if self._st_scope == 'CENAR' or self._st_scope == 'COMER' or self._st_scope == 'TOMAR':
                await self.sender.sendMessage('¿A qué código postal prefieres ir de los que te he comentado?')
            else:
                await self.sender.sendMessage('Necesito saber si quieres ir a comer o a cenar.')
                return
        elif action == 'CP':
            if self._st_cp != 0:
                if self._st_scope == 'CENAR' or self._st_scope == 'COMER' or self._st_scope == 'TOMAR' or self._st_scope == 'TAPAS':
                    df_places = self._list_places(self._st_cp)
                    #text = self.format_for_print2(df_places)
                    text = ''
                    for row in df_places.iterrows():
                        text += str(row[1][0])
                        text += " - "
                        text += str(row[1][1])
                        text += " - "
                        text += str(row[1][2])
                        text += "\n\n"                    
                    await self.sender.sendMessage(text)
                    return
            else:
                await self.sender.sendMessage('Necesito saber a qué código postal de los que te he comentado quieres ir.')
                return
        else:
            await self.sender.sendMessage('Necesito más contexto sobre lo que me estás preguntando.')
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
gmaps = gm.Client(key=sys.argv[2])


bot = telepot.aio.DelegatorBot(TOKEN, [
    pave_event_space()(
        per_chat_id(), create_open, Player, timeout=120),
])

loop = asyncio.get_event_loop()
loop.create_task(bot.message_loop())
print('Listening ...')

loop.run_forever()
