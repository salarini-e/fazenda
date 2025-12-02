from django import template
from django.utils.safestring import mark_safe
# from ..models import Turma, Turno
from django.db.models import Q
from datetime import date

register = template.Library()

