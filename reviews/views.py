from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from providers.models import Provider
from .models import Review

# Если нужны дополнительные view для reviews