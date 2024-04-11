from django.shortcuts import render, redirect
from .forms import ThemeUploadForm

def upload_theme(request):
    if request.method == 'POST':
        form = ThemeUploadForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('/')  # Redirect to home page after successful upload
    else:
        form = ThemeUploadForm()
    return render(request, 'themes/upload_theme.html', {'form': form})
