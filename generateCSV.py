import requests
import csv

#IMPORTANT! Make sure you run this in Python 3.7 or later,
#since this relies on being able to iterate over a dictionary
#in insertion order (this was not the case in 3.6).

#while processing cards, we'll store the number of cards and
#the total number of words in each set in this dictionary,
#so we can retrieve it later using the set code.
cardAndWordCounts = {}

#Use the Scryfall search API to find all cards matching the
#query "-t:conspiracy", which just filters out an old
#obsoleted card type that isn't used anywhere anymore.
#Results sorted by release date, newest to oldest
url = "https://api.scryfall.com/cards/search?order=released&q=-t:conspiracy"

processedCards = 0
#The request doesn't return all of the cards we want. Instead,
#it's paginated; it returns the first 175 cards, and an API link
#to the next page. So we repeatedly get a page, process all of the
#cards on that page, then get the next one.
while(True):
    #get next page from Scryfall API
    resp = requests.get(url).json()
    
    for card in resp["data"]:
        words = 0
        if( "card_faces" in card ):
            #if it's a double sided card, add the number of words
            #on both sides
            for face in card["card_faces"]:
                words += len( face["oracle_text"].split(" ") )
        else:
            words += len( card["oracle_text"].split(" ") )
        
        setCode = card["set"]
        if( setCode in cardAndWordCounts ):
            #If we already have data for the set, add this card
            #to it by adding 1 to the number of cards and
            #increasing the total word count of the set
            cardAndWordCounts[setCode][0] += 1
            cardAndWordCounts[setCode][1] += words
        else:
            #Otherwise, we need to add a new entry to the
            #dictionary, with the data for the current card.
            cardAndWordCounts[setCode] = [1, words]
    
    processedCards += len( resp["data"] )
    print("Processed {}/{} cards".format( processedCards, resp["total_cards"] ) )
    
    if( resp["has_more"] ):
        #if there's another page of results, get the URL for the next page and repeat
        url = resp["next_page"]
    else:
        #we've processed the last page, break out of the loop
        break

averages = []

print("Calculating averages...")
#this iterates over the sets in insertion order,
#starting with the first one inserted (i.e. the newest)
for (set, counts) in cardAndWordCounts.items():
    #only include major sets with more than 30 cards
    if( counts[0] > 30 ):
        averages.append( [ set, counts[1] / counts[0] ] )

print("Writing CSV file...")

#open the file we want to write to
#(the "with" syntax makes sure it automatically closes after)
with open('setAverages.csv', 'w', newline='') as f:
    # create the csv writer
    writer = csv.writer(f, delimiter=' ')

    # write data to the csv file
    writer.writerows(averages)
print("Done! Result saved to setAverages.csv")