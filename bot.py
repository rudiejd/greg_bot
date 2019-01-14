# bot that uses markovify to model how we speak in a group chat
# jd rudie 2018

import requests
import markovify
import re
import operator


# train the bot on corpus file written from group using markovify
def gm_train():
    learning_file = open('gm_msgs.txt', 'r')
    gm_model = markovify.Text(learning_file, state_size=2)
    learning_file.close()
    return gm_model


# send generated message to group
def message(text):
    print(text)
    post_params = {'bot_id': 'YOUR_BOT_ID_HERE', 'text': text}
    requests.post('https://api.groupme.com/v3/bots/post', params=post_params)


def most_words():
    with open('gm_msgs.txt', 'r') as f:
        sf = f.read().strip().replace('@', '').split(' ')

    words = {}
    boring_stuff = ["these", "what", "are", "can", "make", "not", "him", "in", "of", "he", "she", "that", "this", "it",
                    "a", "the", "I", "you", "and", "then", "to", "so", "him", "his", "their", "theirs", "its", "we",
                    "me", "i", "on", "if", "is", "for", "me", "my", "mine", "all", "was", "it's", "what", "are", "can",
                    "but", "He", "say", "Bing", "do", "be"]

    for word in sf:
        if word not in words and re.match(r'\w+', word) and word not in boring_stuff:
            words[word] = 1
        elif word in words:
                words[word] += 1
        else:
            continue
    f.close()
    sorted_words = sorted(words.items(), key=operator.itemgetter(1))
    return sorted_words[-15:]


# main method that checks for messages

def main():
    arr = []
    #blacklisting the bot itself and the GORT bot from writing to bot's corpus
    black_list = ('Greg, GORT')
    while True:


        request_params = {'token': 'YOUR_TOKEN_HERE', 'limit': 1}
        api_return = requests.get('https://api.groupme.com/v3/groups/YOUR_GROUP_ID_HERE/messages', params=request_params).json()
        response_message = str(api_return['response']['messages'][0]['text'])
        sender = api_return['response']['messages'][0]['name']

        at_pattern = re.compile('@')
        url_pattern = re.compile("http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+] |[!*\(\), ]|(?:%[0-9a-fA-F][0-9a-fA-F]))+")
        emoji_pattern = re.compile("["
                                   u"\U0001F600-\U0001F64F"  # emoticons
                                   u"\U0001F300-\U0001F5FF"  # symbols & pictographs
                                   u"\U0001F680-\U0001F6FF"  # transport & map symbols
                                   u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                                   "]+", flags=re.UNICODE)

        response_message = emoji_pattern.sub(r'', response_message)
        response_message = url_pattern.sub(r'', response_message)
        response_message = at_pattern.sub(r'', response_message)
        
        #checks whether sender is in blacklisted users before running command or recording text
        if sender not in black_list:
            #commands for the bot, it only runs one at a time
            if re.match('.*[G|g]reg.*', response_message):
                print("Greg is needed!")
                model = gm_train()
                send_gm = model.make_short_sentence(200)
                arr.append(send_gm)
                message(send_gm)
                    
            elif re.match('.*[T|t]est.*', response_message):
                message("shut the fuck up teddy or teddy's bot")
                arr.append(response_message)

            #give the most used words in a given chat
            elif re.match('.*mostwords.*', response_message):
                most = most_words()
                ret_msg = ""
                message('Count of most used words in this chat:')
                for item in most:
                    ret_msg += item[0] + ': ' + str(item[1]) + '\n'

                message(ret_msg)

            #record a message if it hasn't already been said since the program has been running
            if response_message not in arr and not re.match('.*[G|g]reg.*', response_message):
                f = open('gm_msgs.txt', 'a')
                f.write(str(response_message) + ' ')
                f.close()
                arr.append(response_message)


main()

