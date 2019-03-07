from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.http import Http404
from django.shortcuts import render, redirect

from .forms import ResumeForm, ResumeItemForm
from .models import Resume, ResumeItem


@login_required
def resume_list_view(request):
    """
    Handle a request to show resume list
    """
    resume_list = Resume.objects\
        .filter(user=request.user)\
        .order_by('title')\
        .annotate(resume_count=Count('resumeitem'))

    return render(request, 'resume/resume_list.html', {
        'resume_list': resume_list
    })


@login_required
def resume_create_view(request):
    """
    Handle a request to create a new resume.
    """
    if request.method == 'POST':
        form = ResumeForm(request.POST)
        if form.is_valid():
            new_resume = form.save(commit=False)
            new_resume.user = request.user
            new_resume.title = request.POST.get('title')
            new_resume.save()

            return redirect(resume_list_view)
    else:
        form = ResumeForm()

    return render(request, 'resume/resume_create.html', {'form': form})


@login_required
def resume_view(request, resume_id):
    """
    Handle a request to view a user's resume.
    """
    resume = Resume.objects.get(id__in=resume_id)
    resume_items = ResumeItem.objects\
        .filter(resume=resume_id)\
        .order_by('-start_date')

    return render(request, 'resume/resume.html', {
        'resume_items': resume_items,
        'resume_title': resume.title,
        'resume_id': resume.id
    })


@login_required
def resume_change_name_view(request, resume_id):
    """
    Handle a request to change a resume name.

    :param resume_id: The Database ID of the Resume to be renamed
    """

    try:
        resume_item = Resume.objects.get(id__in=resume_id)
    except ResumeItem.DoesNotExist:
        raise Http404

    template_dict = {'resume_id': resume_id}

    if request.method == 'POST':
        if 'delete' in request.POST:
            resume_item.delete()
            return redirect(resume_list_view)

        form = ResumeForm(request.POST, instance=resume_item)
        if form.is_valid():
            form.save()
            form = ResumeForm(instance=resume_item)
            template_dict['message'] = 'Resume item updated'
    else:
        form = ResumeForm(instance=resume_item)

    template_dict['form'] = form

    return render(request, 'resume/resume_change_name.html', template_dict)


@login_required
def resume_item_create_view(request, resume_id):
    """
    Handle a request to create a new resume item.
    """
    resume = Resume.objects.get(id__in=resume_id)
    if request.method == 'POST':
        form = ResumeItemForm(request.POST)
        if form.is_valid():
            new_resume_item = form.save(commit=False)
            new_resume_item.resume = resume
            new_resume_item.save()

            return redirect(resume_item_edit_view, resume_id, new_resume_item.id)
    else:
        form = ResumeItemForm()

    return render(request, 'resume/resume_item_create.html',
                  {'form': form, 'resume_id': resume_id})


@login_required
def resume_item_edit_view(request, resume_id, resume_item_id):
    """
    Handle a request to edit a resume item.

    :param resume_item_id: The database ID of the ResumeItem to edit.
    :param resume_id: The Database ID of the Resume to filter
    """

    try:
        resume_item = ResumeItem.objects\
            .filter(resume=resume_id)\
            .get(id=resume_item_id)
    except ResumeItem.DoesNotExist:
        raise Http404

    template_dict = {'resume_id': resume_id}

    if request.method == 'POST':
        if 'delete' in request.POST:
            resume_item.delete()
            return redirect(resume_view, resume_id)

        form = ResumeItemForm(request.POST, instance=resume_item)
        if form.is_valid():
            form.save()
            form = ResumeItemForm(instance=resume_item)
            template_dict['message'] = 'Resume item updated'
    else:
        form = ResumeItemForm(instance=resume_item)

    template_dict['form'] = form

    return render(request, 'resume/resume_item_edit.html', template_dict)
