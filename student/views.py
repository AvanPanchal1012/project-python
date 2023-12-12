import random

from django.shortcuts import render,redirect,reverse
from . import forms,models
from django.db.models import Sum
from django.contrib.auth.models import Group
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required,user_passes_test
from django.conf import settings
from datetime import date, timedelta
from quiz import models as QMODEL
from teacher import models as TMODEL


#for showing signup/login button for student
def studentclick_view(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect('afterlogin')
    return render(request,'student/studentclick.html')

def student_signup_view(request):
    userForm=forms.StudentUserForm()
    studentForm=forms.StudentForm()
    mydict={'userForm':userForm,'studentForm':studentForm}
    if request.method=='POST':
        userForm=forms.StudentUserForm(request.POST)
        studentForm=forms.StudentForm(request.POST,request.FILES)
        if userForm.is_valid() and studentForm.is_valid():
            user=userForm.save()
            user.set_password(user.password)
            user.save()
            student=studentForm.save(commit=False)
            student.user=user
            student.save()
            my_student_group = Group.objects.get_or_create(name='STUDENT')
            my_student_group[0].user_set.add(user)
        return HttpResponseRedirect('studentlogin')
    return render(request,'student/studentsignup.html',context=mydict)

def is_student(user):
    return user.groups.filter(name='STUDENT').exists()

@login_required(login_url='studentlogin')
@user_passes_test(is_student)
def student_dashboard_view(request):
    dict={
    
    'total_course':QMODEL.Course.objects.all().count(),
    'total_question':QMODEL.Question.objects.all().count(),
    }
    return render(request,'student/student_dashboard.html',context=dict)

@login_required(login_url='studentlogin')
@user_passes_test(is_student)
def student_exam_view(request):
    courses=QMODEL.Course.objects.all()
    return render(request,'student/student_exam.html',{'courses':courses})

@login_required(login_url='studentlogin')
@user_passes_test(is_student)
def take_exam_view(request):
    total_questions=5

    return render(request,'student/take_exam.html',{'total_questions':total_questions,'total_marks':total_questions})

@login_required(login_url='studentlogin')
@user_passes_test(is_student)
def start_exam_view(request):

    num_entities = QMODEL.Question.objects.all().count()

    rand_entities = []
    while len(rand_entities) < 5:
        num = random.randint(1, num_entities)
        if not num in rand_entities:
            rand_entities.append(num)

    questions = QMODEL.Question.objects.filter(id__in=rand_entities)

    ids = []
    for i in questions:
        ids.append(i.id)

    if request.method=='POST':
        pass
    response= render(request,'student/start_exam.html',{'questions':questions})
    response.set_cookie('question_ids', ','.join([str(elem) for elem in ids]))
    return response


@login_required(login_url='studentlogin')
@user_passes_test(is_student)
def calculate_marks_view(request):

    if request.COOKIES.get('question_ids') is not None:
        question_id = request.COOKIES.get('question_ids')

        total_marks=0
        questions=QMODEL.Question.objects.all().filter(id__in=question_id.split(','))
        course = QMODEL.Course.objects.get(id=1)

        print(questions.query)

        for i in range(len(questions)):
            selected_ans = request.COOKIES.get(str(i+1))
            actual_answer = questions[i].answer
            if selected_ans == actual_answer:
                total_marks = total_marks + 1
        print("studentdata", request.user.id)
        student = models.Student.objects.get(user_id=request.user.id)
        result = QMODEL.Result()
        result.marks=total_marks
        result.exam=course
        result.student=student

        result.save()

        return HttpResponseRedirect('view-result')



@login_required(login_url='studentlogin')
@user_passes_test(is_student)
def view_result_view(request):
    print('userid',request.user.id)
    user_id = 1
    if request.user.id == 1:
        user_id = 1;
    else:
        user_id = request.user.id - 1
    last_exam = QMODEL.Result.objects.filter(student_id=user_id).latest('id')

    result = 'Please try again!'

    if last_exam.marks == 3:
        result = 'Good job!'
    elif last_exam.marks == 4:
        result = 'Excellent work!'
    elif last_exam.marks == 5:
        result = 'You are a genius!'

    return render(request,'student/view_result.html',{'result':result, 'last_exam': last_exam})
    

@login_required(login_url='studentlogin')
@user_passes_test(is_student)
def check_marks_view(request):
    student = models.Student.objects.get(user_id=request.user.id)
    results= QMODEL.Result.objects.all().filter(exam=1).filter(student=student)

    average = 0
    highest_marks = float('-inf')
    lowest_marks = float('inf')

    for result in results:
        marks = result.marks

        if marks > highest_marks:
            highest_marks = marks

        if marks < lowest_marks:
            lowest_marks = marks
    for i in results:
        average += i.marks


    return render(request,'student/check_marks.html',{'results':results, 'avg': average / results.count(),'max':highest_marks,'min':lowest_marks})

@login_required(login_url='studentlogin')
@user_passes_test(is_student)
def student_marks_view(request):
    courses=QMODEL.Course.objects.all()
    return render(request,'student/student_marks.html',{'courses':courses})
  