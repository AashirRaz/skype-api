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

            # Create a unique cache key based on the username
            cache_key = f'skype_contacts_{skype_username}'
            cached_contacts = cache.get(cache_key)

            if cached_contacts is not None:
                return JsonResponse({'contacts': cached_contacts})

            # Log in to Skype
            sk = Skype(skype_username, skype_password)  # Skype object

            # Fetch contacts
            chats = {}

            def fetch_chats():
                nonlocal chats
                for i in range(20):  # Reduced to 5 sets of recent chats
                    chats.update(sk.chats.recent())

            # Run fetch_chats in parallel
            thread = threading.Thread(target=fetch_chats)
            thread.start()
            thread.join()  # Wait for the thread to complete

            conversations = {}

            for i in chats.values():
                if isinstance(i, chat.SkypeSingleChat) and bool(i.user and i.user.name and i.user.name.first):
                    conversations[i.id] = i.user.name.first + " " + (i.user.name.last if i.user.name.last else "")
                elif isinstance(i, chat.SkypeGroupChat) and bool(i.topic):
                    conversations[i.id] = i.topic

            # Cache the results for 5 minutes (300 seconds)
            cache.set(cache_key, conversations, 300)

            return JsonResponse({'contacts': conversations})
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON.'}, status=400)
        except KeyError:
            return JsonResponse({'error': 'Missing username or password.'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    else:
        return JsonResponse({'error': 'Invalid request method.'}, status=400)
