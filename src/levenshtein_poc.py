#LEVENSHTEIN COMMAND SUGGESTION POC FOR EQUINOX 2017 JAVIER CARRO & CO PROJECT :)

from nltk.metrics import edit_distance

list_available_options = ["AYUDA","COMPRAS","SALDO","LUGARES","SALIR"]

list_simulated_commands = ["AYUDAME","FUERA","SALDO","LUGARES","COMPRAR","COMPRAS","LURAGES","LUGRAES","SALDIR"]

dictionary=dict()
for command in list_simulated_commands:
    
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

        leven_coeff = edit_distance (key,value,substitution_cost=1, transpositions=True)
        
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
        
    
            
        
            
        
        
        
