import json
import requests

from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views import View
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt


class TasksList(View):

    http_method_names = ['get']

    def get(self, request):
        try:
            response = requests.get(settings.ARTHUR_SERVER + "/tasks")
            tasks = json.loads(response.text)['tasks']
        except requests.exceptions.RequestException:
            err = "Impossible connect to Arthur"
            return JsonResponse({'status': 'false', 'message': err},
                                status=500)
        except json.decoder.JSONDecodeError:
            err = "Error parsing response, please check the KingArthur url"
            return JsonResponse({'status': 'false', 'message': err},
                                status=500)
        return JsonResponse(tasks, safe=False)


class Task(View):

    http_method_names = ['get']

    def get(self, request, task_id):
        try:
            response = requests.get(settings.ARTHUR_SERVER +
                                    "/task/{}".format(task_id))
            task = json.loads(response.text)
        except requests.exceptions.RequestException:
            err = "Impossible connect to Arthur"
            return JsonResponse({'status': 'false', 'message': err},
                                status=500)
        except json.decoder.JSONDecodeError:
            err = "Task not found, please check the task ID"
            return JsonResponse({'status': 'false', 'message': err},
                                status=500)
        return JsonResponse(task, safe=False)


class AddTask(View):
    http_method_names = ['post']

    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super(AddTask, self).dispatch(*args, **kwargs)

    def post(self, request):
        task_data = json.loads(request.body)['taskData']
        task_to_add = {
          'tasks': [{}]
        }
        task_to_add['tasks'][0]['task_id'] = task_data['task_id']
        task_to_add['tasks'][0]['backend'] = task_data['backendSelected']
        task_to_add['tasks'][0]['backend_args'] = {}
        if task_data['backendSelected'] == 'git':
            task_to_add['tasks'][0]['backend_args'] = {
                'gitpath': task_data['gitBackendArgs']['gitPath'],
                'uri': task_data['gitBackendArgs']['uri'],
            }
            if 'fromDate' in task_data['gitBackendArgs']:
                task_to_add['tasks'][0]['backend_args']['from_date'] = \
                    task_data['gitBackendArgs']['fromDate']
        elif task_data['backendSelected'] == 'bugzillarest':
            task_to_add['tasks'][0]['backend_args'] = {
                'url': task_data['bugzillarestBackendArgs']['url'],
            }
            if 'fromDate' in task_data['bugzillarestBackendArgs']:
                task_to_add['tasks'][0]['backend_args']['from_date'] = \
                    task_data['bugzillarestBackendArgs']['fromDate']
        task_to_add['tasks'][0]['category'] = task_data['category']
        task_to_add['tasks'][0]['scheduler'] = {
            'delay': int(task_data['schedulerArgs']['delay']),
            'max_retries': int(task_data['schedulerArgs']['maxRetries'])
        }

        response = requests.post(url=settings.ARTHUR_SERVER + "/add",
                                 json=task_to_add)
        if response.status_code != 200:
            err = "Error adding the task to KingArthur"
            return JsonResponse({'status': 'false', 'message': err},
                                status=500)
        return JsonResponse({'status': 'ok',
                             'message': "Task added correctly"}, safe=False)
