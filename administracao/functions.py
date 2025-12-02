import random
import string
from django.contrib.auth.models import Group
from django.forms import ValidationError


def generateToken(id):
    token = str(id)
    token += ''.join(random.choices(string.ascii_uppercase + string.digits, k=9))
    return token

def user_group_loja(request):
    user = request.user
    if user.is_authenticated:
        belongs_to_group = user.groups.filter(name='bemestaranimal_lojas').exists()
    else:
        belongs_to_group = False
    return {'user_belongs_to_group': belongs_to_group}
