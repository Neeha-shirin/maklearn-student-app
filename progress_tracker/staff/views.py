from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.models import User
from django.contrib import messages
from review.models import HelpRequest
from learning.models import Module, Task, StudentTask, StudentCurrentModule
from app1.models import dbstudent1



@user_passes_test(lambda u: u.is_authenticated and u.is_staff, login_url='/app1/teacherlogin/')
def staff_dashboard_view(request):
    student_users = User.objects.filter(is_staff=False)
    students = []

    for student in student_users:
        student_module_obj = StudentCurrentModule.objects.filter(student=student).first()
        current_module = student_module_obj.module if student_module_obj else None

        if current_module:
            tasks = Task.objects.filter(module=current_module)
            total_tasks = tasks.count()
            completed_tasks = StudentTask.objects.filter(student=student, task__in=tasks, is_completed=True).count()
        else:
            total_tasks = 0
            completed_tasks = 0

        progress = int((completed_tasks / total_tasks) * 100) if total_tasks else 0

        if progress >= 75:
            status = "On Track"
        elif progress >= 40:
            status = "Needs Help"
        else:
            status = "Behind Schedule"

        students.append({
            'student': student,
            'current_module': current_module.name if current_module else "No Module",
            'current_module_week': current_module.week if current_module else None,
            'completed': completed_tasks,
            'total': total_tasks,
            'progress': progress,
            'status': status,
        })

    help_requests = HelpRequest.objects.select_related('student', 'accepted_by').order_by('-created_at')

    return render(request, 'staff/staff.html', {
        'students': students,
        'help_requests': help_requests,
    })


@user_passes_test(lambda u: u.is_authenticated and u.is_staff, login_url='/app1/teacherlogin/')
def accept_help_request(request, request_id):
    help_request = get_object_or_404(HelpRequest, id=request_id)
    if not help_request.accepted_by:
        help_request.accepted_by = request.user
        help_request.save()
    return redirect('staff_dashboard')


@user_passes_test(lambda u: u.is_authenticated and u.is_staff, login_url='/app1/teacherlogin/')
def mark_request_handled(request, request_id):
    help_request = get_object_or_404(HelpRequest, id=request_id)
    if help_request.accepted_by == request.user:
        help_request.is_handled = True
        help_request.save()
    return redirect('staff_dashboard')

@user_passes_test(lambda u: u.is_authenticated and u.is_staff, login_url='/app1/teacherlogin/')
def approve_next_week(request, student_id):
    student = get_object_or_404(User, id=student_id, is_staff=False)

    # Get student's course(s) - assuming one course per student_profile
    try:
        student_profile = dbstudent1.objects.get(s_email=student.email)
        course = student_profile.course
    except dbstudent1.DoesNotExist:
        messages.error(request, "Student profile or course not found.")
        return redirect('staff_dashboard')

    # Get modules only for that course, ordered by week
    modules = list(Module.objects.filter(course=course).order_by('week'))
    student_module_obj, created = StudentCurrentModule.objects.get_or_create(student=student, course=course)

    if not student_module_obj.module:
        if modules:
            student_module_obj.module = modules[0]
            student_module_obj.save()
            messages.success(request, f"Assigned first module '{modules[0].name}' to {student.username}.")
        else:
            messages.error(request, "No modules found.")
        return redirect('staff_dashboard')

    current_module = student_module_obj.module
    tasks = Task.objects.filter(module=current_module)
    total_tasks = tasks.count()
    completed_tasks = StudentTask.objects.filter(student=student, task__in=tasks, is_completed=True).count()

    if completed_tasks < total_tasks:
        messages.error(request, f"{student.username} has not completed all tasks in '{current_module.name}' (completed {completed_tasks} of {total_tasks}).")
        return redirect('staff_dashboard')

    try:
        current_index = modules.index(current_module)
    except ValueError:
        messages.error(request, "Current module not found in module list.")
        return redirect('staff_dashboard')

    if current_index + 1 < len(modules):
        next_module = modules[current_index + 1]
        student_module_obj.module = next_module
        student_module_obj.save()
        messages.success(request, f"Moved {student.username} to next module: '{next_module.name}'.")
    else:
        messages.info(request, f"{student.username} is already on the final module.")

    return redirect('staff_dashboard')


@user_passes_test(lambda u: u.is_authenticated and u.is_staff, login_url='/app1/teacherlogin/')
def student_module_progress(request, student_id):
    student = get_object_or_404(User, id=student_id, is_staff=False)
    modules = Module.objects.all()
    module_progress = []

    for module in modules:
        total_tasks = module.tasks.count()
        completed_tasks = StudentTask.objects.filter(
            student=student,
            task__module=module,
            is_completed=True
        ).count()

        if completed_tasks == total_tasks and total_tasks > 0:
            status = "Completed"
        elif completed_tasks > 0:
            status = "In Progress"
        else:
            status = "Not Started"

        module_progress.append({
            "name": module.name,
            "status": status
        })

    return render(request, 'staff/student_module_progress.html', {
        "progress": {
            "student_id": student.id,
            "modules": module_progress
        }
    })
