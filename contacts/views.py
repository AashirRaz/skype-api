# contacts/views.py
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.cache import cache
import json
from skpy import Skype, chat
import threading

@csrf_exempt
def get_skype_contacts(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            skype_username = data['username']
            skype_password = data['password']

            # Log in to Skype
            sk = Skype(skype_username, skype_password)  # Skype object

            # Fetch contacts
            chats = {}
            for i in range(3):  # Reduced to 5 sets of recent chats
                chats.update(sk.chats.recent())

            conversations = {}

            for i in chats.values():
                if isinstance(i, chat.SkypeSingleChat) and bool(i.user and i.user.name and i.user.name.first):
                    conversations[i.id] = i.user.name.first + " " + (i.user.name.last if i.user.name.last else "")
                elif isinstance(i, chat.SkypeGroupChat) and bool(i.topic):
                    conversations[i.id] = i.topic

            return JsonResponse({'contacts': conversations})
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON.'}, status=400)
        except KeyError:
            return JsonResponse({'error': 'Missing username or password.'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    else:
        return JsonResponse({'error': 'Invalid request method.'}, status=400)
@csrf_exempt
def send_skype_message(request):
     if request.method == 'POST':
        try:    
            data = json.loads(request.body)
            skype_username = data['username']
            skype_password = data['password']
            message = data['message']

            skypeLiveIds = data['liveIds']
            # Log in to Skype
            sk = Skype(skype_username, skype_password)


            SendMsgToSkype(sk, message, skypeLiveIds)

            return JsonResponse({'success': 'Message sent successfully.'})

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON.'}, status=400)
        except KeyError:
            return JsonResponse({'error': 'Missing username or password.'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
        

def SendMsgToSkype(sk:Skype, message, liveIds: list[str]):
        for contact in liveIds:
            threading.Thread(target=sendMessagesInParallel, args=(sk ,contact, message)).start()

def sendMessagesInParallel(sk: Skype, contact, message):
        ch:chat.SkypeChat = sk.chats.chat(contact)
        ch.sendMsg(message)